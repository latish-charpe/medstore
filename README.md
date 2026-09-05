# MedStore

MedStore is a Flask-based online medicine store with customer shopping, store-manager inventory management, order processing, healthcare browsing, and symptom guidance. It uses MongoDB for document persistence.

> **Medical disclaimer:** The symptom checker provides general information and over-the-counter guidance only. It is not a diagnosis or a substitute for a qualified doctor or pharmacist. Seek urgent medical care for emergency symptoms.

## Features

- Customer registration, login, cart, checkout, and order confirmation
- Store-manager registration, authentication, inventory isolation, and dashboard
- Add, update, and delete medicines with category, stock, expiry, formulation, image, and composition data
- Medicine search by name or composition, category filtering, and medicine-type filtering
- Category-based healthcare browsing
- Order splitting by store manager for multi-store inventory
- Order status management: `Placed`, `Packed`, `Delivered`, and `Cancelled`
- Prescription upload flow for pharmacist review
- Rule-based symptom guidance with an optional Gemini Health Assistant integration
- Responsive web interface built with Jinja templates and custom CSS
- MongoDB-backed persistence with integer application IDs for existing route compatibility
- Deployment configuration for Gunicorn and Vercel

## Tech Stack

- Python 3
- Flask
- PyMongo
- Flask-Login
- MongoDB
- Jinja2 templates
- Gunicorn for production-style serving
- Optional Google Gemini API integration

## Requirements

- Python 3.10 or newer
- `pip`
- MongoDB 5.0+ or a MongoDB Atlas cluster
- Optional: Gemini API key for external health-assistant responses

## Quick Start

1. Clone the repository and enter the project directory.

   ```bash
   git clone <repository-url>
   cd medstore
   ```

2. Create and activate a virtual environment.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Start MongoDB locally with Docker Compose.

   ```bash
   docker compose up -d mongodb
   ```

   Or set `MONGODB_URI` to a reachable MongoDB Atlas connection string.

   For Atlas, make sure the database user exists, the cluster is running, and the
   current deployment or Codespaces egress IP is included in **Security > Network
   Access**. Atlas access lists are IP-based; `127.0.0.1` is not the public IP of
   your development environment.

5. Start the development server.

   ```bash
   python app.py
   ```

6. Open [http://localhost:5001](http://localhost:5001).

On first startup, the application connects to MongoDB, creates the required collections as data is written, creates the default categories, and seeds the default store-manager inventory when needed.

To stop the local MongoDB container after development:

```bash
docker compose down
```

## Configuration

The application works locally with the built-in defaults, but production deployments should provide environment variables:

| Variable | Required | Description |
| --- | --- | --- |
| `MONGODB_URI` | No | MongoDB connection string. Defaults to `mongodb://localhost:27017`. |
| `MONGODB_DB` | No | MongoDB database name. Defaults to `medstore`. |
| `SECRET_KEY` | Recommended | Secret that should be used to sign Flask sessions. Replace the current development fallback before production deployment. |
| `GEMINI_API_KEY` | No | Enables Gemini-backed responses in the store-manager health assistant. Without it, the local rules-based assistant is used. |
| `GEMINI_MODEL` | No | Gemini model name. Defaults to `gemini-3.6-flash`. |
| `PORT` | No | Port used by `app.py`. Defaults to `5001`. |

Example local configuration:

```bash
export SECRET_KEY="replace-with-a-long-random-value"
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DB="medstore"
# Optional:
# export GEMINI_API_KEY="your-api-key"
# export GEMINI_MODEL="gemini-3.6-flash"
python app.py
```

Do not commit API keys, production secrets, or a production MongoDB URI to the repository.

## User Flows

### Customers

1. Register at `/register` or log in at `/login`.
2. Browse `/medicines` or `/healthcare`.
3. Add available medicines to the cart.
4. Complete the delivery address and payment selection at checkout.
5. Review the order confirmation.

### Store managers

1. Use `/register-manager` with the manager secret code, or use an existing manager account.
2. Log in through `/manager-login`.
3. Manage inventory and categories from `/dashboard`.
4. Review manager-owned orders and update their status.
5. Use the manager-only Health Assistant API from the dashboard.

The development seed creates a manager named `virat` with the password configured in the current application seed logic. Change or remove seeded credentials before deploying to a shared or production environment.

## Health Assistant

The public symptom checker is available at `/symptom-checker` and uses local symptom rules by default. When `GEMINI_API_KEY` is configured, the application attempts to use Gemini and falls back to the local assistant if the request fails.

The manager-only endpoint is:

```text
POST /api/health-chat
```

It expects a JSON body such as:

```json
{"message": "I have a mild headache"}
```

Responses are informational only and include a medical disclaimer.

## Database

The application stores data in the MongoDB database configured by `MONGODB_URI` and `MONGODB_DB`. The MongoDB adapter and document models are defined in `models.py`.

Collections are created automatically by MongoDB when the application first writes data. The application uses the collections `users`, `categories`, `medicines`, `orders`, `order_items`, and `customer_queries`.

For legacy inventory that needs to be assigned to the default manager, review the maintenance scripts before running them:

```bash
python assign_legacy_meds.py
python verify_virat.py
```

Do not use destructive maintenance scripts against production data without a MongoDB backup.

## Testing and Verification

Install the dependencies first, then run the automated tests:

```bash
python -m pytest
```

Focused tests can be run individually:

```bash
python -m pytest test_improved_search.py
python -m pytest test_medical_use_restoration.py
python -m pytest test_register_debug.py
python -m pytest test_symptom_checker.py
```

The repository also contains targeted verification scripts for inventory isolation, orders, purchase flow, categories, configuration, and seeded data. Most are executable Python scripts, for example:

```bash
python verify_isolation.py
python verify_orders.py
python verify_purchase_flow.py
```

## Project Structure

```text
app.py                 Flask application, routes, startup, and seed logic
models.py              MongoDB document models and query compatibility layer
health_assistant.py    Gemini integration and local fallback handling
medicines_data.py      Starter medicine catalog
requirements.txt       Python dependencies
Procfile               Gunicorn process definition
vercel.json            Vercel deployment configuration
templates/             Jinja HTML templates
static/css/            Application styles
test_*.py              Automated tests
verify_*.py            Targeted verification scripts
```

