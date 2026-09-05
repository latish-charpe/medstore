from datetime import date, datetime, timedelta
import os

from flask import abort
from flask_login import UserMixin
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
from pymongo.errors import ServerSelectionTimeoutError


class Condition:
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value

    def matches(self, document):
        current = self.field.resolve(document)
        if self.operator == 'eq':
            return current == self.value
        if self.operator == 'ne':
            return current != self.value
        if self.operator == 'ilike':
            return self.value.strip('%').lower() in str(current or '').lower()
        return False


class Field:
    def __init__(self, owner, name):
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        if getattr(instance, '_persisted', False):
            db.session.mark_dirty(instance)

    def resolve(self, document):
        if self.owner is None or isinstance(document, self.owner):
            return getattr(document, self.name, None)
        if hasattr(document, 'related_value'):
            return document.related_value(self.owner, self.name)
        return None

    def __eq__(self, value):
        return Condition(self, 'eq', value)

    def __ne__(self, value):
        return Condition(self, 'ne', value)

    def ilike(self, value):
        return Condition(self, 'ilike', value)

    def desc(self):
        return Sort(self, DESCENDING)

    def asc(self):
        return Sort(self, ASCENDING)


class Sort:
    def __init__(self, field, direction):
        self.field = field
        self.direction = direction


class OrCondition:
    def __init__(self, conditions):
        self.conditions = conditions

    def matches(self, document):
        return any(condition.matches(document) for condition in self.conditions)


class QuerySet:
    def __init__(self, model, conditions=None, sort=None):
        self.model = model
        self.conditions = conditions or []
        self.sort = sort

    def _clone(self, conditions=None, sort=None):
        return QuerySet(
            self.model,
            self.conditions + (conditions or []),
            sort if sort is not None else self.sort,
        )

    def _documents(self):
        documents = list(db.collection(self.model._collection_name).find({}))
        objects = [self.model._from_document(document) for document in documents]
        for condition in self.conditions:
            objects = [obj for obj in objects if condition.matches(obj)]
        if self.sort:
            objects.sort(
                key=lambda obj: self.sort.field.resolve(obj) or '',
                reverse=self.sort.direction == DESCENDING,
            )
        return objects

    def filter_by(self, **kwargs):
        return self._clone([
            Condition(Field(self.model, key), 'eq', value)
            for key, value in kwargs.items()
        ])

    def filter(self, *conditions):
        return self._clone(list(conditions))

    def join(self, _model):
        return self

    def order_by(self, sort):
        return self._clone(sort=sort)

    def all(self):
        return self._documents()

    def first(self):
        objects = self._documents()
        return objects[0] if objects else None

    def count(self):
        return len(self._documents())

    def get(self, identifier):
        try:
            identifier = int(identifier)
        except (TypeError, ValueError):
            return None
        return self.filter_by(id=identifier).first()

    def get_or_404(self, identifier):
        result = self.get(identifier)
        if result is None:
            abort(404)
        return result

    def delete(self):
        deleted = 0
        for obj in self._documents():
            db.session.delete(obj)
            deleted += 1
        return deleted


class QueryDescriptor:
    def __get__(self, instance, owner):
        return QuerySet(owner)


class Session:
    def __init__(self):
        self.pending = []
        self.dirty = set()
        self.deleted = []

    def add(self, model):
        if getattr(model, 'id', None) is None:
            model.id = db.next_id(model._collection_name)
        if model not in self.pending:
            self.pending.append(model)

    def bulk_save_objects(self, models):
        for model in models:
            self.add(model)

    def delete(self, model):
        self.deleted.append(model)

    def mark_dirty(self, model):
        self.dirty.add(model)

    def _save(self, model):
        db.collection(model._collection_name).replace_one(
            {'id': model.id}, model.to_document(), upsert=True
        )
        model._persisted = True

    def flush(self):
        for model in self.pending:
            self._save(model)
        self.pending.clear()

    def commit(self):
        self.flush()
        for model in self.dirty:
            self._save(model)
        for model in self.deleted:
            db.collection(model._collection_name).delete_one({'id': model.id})
            model._persisted = False
        self.dirty.clear()
        self.deleted.clear()

    def rollback(self):
        self.pending.clear()
        self.dirty.clear()
        self.deleted.clear()

    def remove(self):
        self.rollback()


class MongoDatabase:
    def __init__(self):
        self.session = Session()
        self.client = None
        self.database = None

    def init_app(self, _app):
        return None

    def connect(self):
        if self.database is None:
            uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
            name = os.getenv('MONGODB_DB', 'medstore')
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            try:
                self.client.admin.command('ping')
            except ServerSelectionTimeoutError as error:
                self.client.close()
                self.client = None
                details = str(error)
                if 'SSL handshake failed' in details or 'TLS' in details:
                    message = (
                        'MongoDB Atlas TLS connection failed. Check that this '
                        'environment IP is allowed in Atlas Network Access, the '
                        'cluster is running, and the workspace network allows '
                        'outbound TLS connections to MongoDB.'
                    )
                else:
                    message = (
                        'MongoDB is unavailable. Start MongoDB locally or set '
                        'MONGODB_URI to a reachable MongoDB Atlas connection string.'
                    )
                raise RuntimeError(
                    f'{message} Connection detail: {details.split(" (configured")[0]}'
                ) from error
            self.database = self.client[name]
        return self.database

    def collection(self, name):
        return self.connect()[name]

    def next_id(self, collection):
        counter = self.connect()['_counters'].find_one_and_update(
            {'_id': collection}, {'$inc': {'value': 1}}, upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return counter['value']

    def create_all(self):
        self.connect()

    def drop_all(self):
        for collection in ('users', 'categories', 'medicines', 'orders', 'order_items', 'customer_queries'):
            self.collection(collection).drop()

    def or_(self, *conditions):
        return OrCondition(conditions)


db = MongoDatabase()


class Document:
    query = QueryDescriptor()
    _fields = ()

    def __init__(self, **values):
        self._persisted = False
        for field in self._fields:
            setattr(self, field, values.get(field))

    @classmethod
    def _from_document(cls, document):
        values = {field: document.get(field) for field in cls._fields}
        if cls is Medicine and isinstance(values.get('expiry_date'), datetime):
            values['expiry_date'] = values['expiry_date'].date()
        object_ = cls(**values)
        object_._persisted = True
        return object_

    def to_document(self):
        document = {field: getattr(self, field, None) for field in self._fields}
        if isinstance(document.get('expiry_date'), date) and not isinstance(document['expiry_date'], datetime):
            document['expiry_date'] = datetime.combine(document['expiry_date'], datetime.min.time())
        return document

    def related_value(self, owner, field):
        if owner is type(self):
            return getattr(self, field, None)
        return None


class User(UserMixin, Document):
    _collection_name = 'users'
    _fields = ('id', 'username', 'password_hash', 'role', 'store_id')
    id = Field(None, 'id')
    username = Field(None, 'username')
    role = Field(None, 'role')

    def __init__(self, **values):
        values.setdefault('role', 'customer')
        values.setdefault('store_id', 'medstore_main')
        super().__init__(**values)

    def get_id(self):
        return str(self.id)

    @property
    def orders(self):
        return Order.query.filter_by(user_id=self.id).all()

    @property
    def managed_orders(self):
        return Order.query.filter_by(store_manager_id=self.id).all()


class Category(Document):
    _collection_name = 'categories'
    _fields = ('id', 'name')
    id = Field(None, 'id')
    name = Field(None, 'name')

    @property
    def medicines(self):
        return Medicine.query.filter_by(category_id=self.id).all()


class Medicine(Document):
    _collection_name = 'medicines'
    _fields = ('id', 'name', 'price', 'quantity', 'expiry_date', 'availability', 'category_id', 'user_id', 'medicine_type', 'unit', 'image_url', 'composition')
    id = Field(None, 'id')
    name = Field(None, 'name')
    composition = Field(None, 'composition')
    medicine_type = Field(None, 'medicine_type')
    user_id = Field(None, 'user_id')

    def __init__(self, **values):
        values.setdefault('availability', True)
        values.setdefault('medicine_type', 'Tablet')
        values.setdefault('unit', 'Strip')
        super().__init__(**values)

    @property
    def category(self):
        return Category.query.get(self.category_id)

    @property
    def expiry_status(self):
        today = date.today()
        if self.expiry_date < today:
            return 'Expired'
        if self.expiry_date <= today + timedelta(days=60):
            return 'Near Expiry'
        return 'Safe'

    def related_value(self, owner, field):
        if owner is Category and field == 'name':
            category = self.category
            return category.name if category else None
        return super().related_value(owner, field)


class Order(Document):
    _collection_name = 'orders'
    _fields = ('id', 'user_id', 'order_date', 'total_amount', 'status', 'payment_method', 'store_manager_id', 'full_name', 'mobile_number', 'address_line1', 'area_landmark', 'city', 'state', 'pincode')
    id = Field(None, 'id')
    order_date = Field(None, 'order_date')
    status = Field(None, 'status')
    user_id = Field(None, 'user_id')
    store_manager_id = Field(None, 'store_manager_id')

    def __init__(self, **values):
        values.setdefault('order_date', datetime.utcnow())
        values.setdefault('status', 'Placed')
        super().__init__(**values)

    @property
    def items(self):
        return OrderItem.query.filter_by(order_id=self.id).all()

    @property
    def buyer(self):
        return User.query.get(self.user_id)

    @property
    def manager(self):
        return User.query.get(self.store_manager_id)


class OrderItem(Document):
    _collection_name = 'order_items'
    _fields = ('id', 'order_id', 'medicine_id', 'medicine_name', 'quantity', 'price')
    id = Field(None, 'id')
    order_id = Field(None, 'order_id')

    @property
    def order(self):
        return Order.query.get(self.order_id)


class CustomerQuery(Document):
    _collection_name = 'customer_queries'
    _fields = ('id', 'user_id', 'name', 'email', 'subject', 'message', 'status', 'created_at')
    id = Field(None, 'id')

    def __init__(self, **values):
        values.setdefault('status', 'New')
        values.setdefault('created_at', datetime.utcnow())
        super().__init__(**values)


for model in (User, Category, Medicine, Order, OrderItem, CustomerQuery):
    for field_name in model._fields:
        field = getattr(model, field_name, None)
        if not isinstance(field, Field):
            field = Field(model, field_name)
            setattr(model, field_name, field)
        field.owner = model
