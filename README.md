# SilentGuard — Advanced Financial Security Platform

**Built by GirlCoders in Uganda**

SilentGuard is a comprehensive fraud detection and personal finance management platform designed for mobile money users in Uganda. It combines ML-powered scam detection, savings tracking, and investment recommendations into a single secure application.

---

## 🚀 What's New (Advanced Upgrades)

### 1. **ML-Powered Scam Detection**
- **TF-IDF + Naive Bayes** classifier when scikit-learn is available
- **Weighted keyword scoring** fallback system (works without ML libraries)
- **Confidence scoring** (0-100%) with risk levels: High, Medium, Low, Safe
- **Trusted sender whitelist** (banks, telcos automatically marked safe)
- **Blacklist integration** — reported numbers boost scam confidence
- **Training data** — 12 scam samples + 10 safe samples for ML model

### 2. **Complete Transaction Recording**
- All deposits, withdrawals, and savings transfers are now logged
- Transaction history with category breakdown
- Summary stats: Total In, Total Out, Transaction Count
- Visual spending breakdown by category

### 3. **Enhanced Dashboard**
- Real-time stats: messages scanned, scams detected, reports filed
- Recent scans preview
- Improved fraud detection card with inline scanning
- Better alert system

### 4. **Upgraded Profile Page**
- Editable user information (email, phone, location)
- Account statistics: scans, scams caught, reports made
- Bank account balance display
- Clean, modern UI with Font Awesome icons

### 5. **Activity Log (Fixed)**
- Now a proper view (was broken before)
- Shows all suspicious security events
- Geolocation tracking via IP
- Event type, location, timestamp, and notes

### 6. **Spending Analytics**
- Interactive Chart.js doughnut chart on savings dashboard
- Category-wise spending breakdown
- Visual representation of where money goes

### 7. **Security Improvements**
- Proper `@login_required` decorators on all sensitive views
- Account locking uses `set_unusable_password()` (admin must reset)
- Suspicious activity logging with geolocation
- Rate limiting ready (django-ratelimit installed)

### 8. **Code Quality**
- Removed duplicate `receive_sms` function
- Fixed broken `activity_log` view
- Proper error handling throughout
- Consistent transaction recording
- Better form validation

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Navigate to project
cd silentguard

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000`

---

## 🔧 Configuration

### Email (Gmail SMTP)
Edit `silentguard/settings.py`:
```python
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"  # Use Gmail App Password
```

### Africa's Talking (SMS)
```python
AFRICASTALKING_USERNAME = 'sandbox'  # or your username
AFRICASTALKING_API_KEY = 'your-api-key'
```

---

## 🎯 Features

### Fraud Detection
- **SMS Scanning**: Paste any message to check for scam indicators
- **ML Analysis**: TF-IDF vectorization + Naive Bayes classification
- **Keyword Detection**: 40+ high-risk and medium-risk keywords
- **Blacklist Check**: Cross-reference against reported numbers
- **Confidence Scoring**: 0-100% scam probability
- **Risk Levels**: High (70%+), Medium (40-69%), Low (20-39%), Safe (<20%)

### Financial Management
- **Bank Accounts**: Virtual accounts with balance tracking
- **Deposits & Withdrawals**: Full transaction recording
- **Savings Goals**: Set targets, track progress with AI feedback
- **Transaction History**: Complete audit trail with category breakdown
- **Spending Analytics**: Visual charts showing spending patterns

### Investment Recommendations
- Triggered at 50% savings goal completion
- Categories: Investment, Insurance, Real Estate, Vehicle Financing, Shares
- Risk levels: Low, Moderate, High
- Expected return rates displayed

### Security
- Account locking for suspicious activity
- Login confirmation system
- Activity logging with geolocation
- Email alerts for fraud reports
- Blacklist management

### Educational Content
- Fraud prevention resources
- Multi-language support capability
- User feedback system

---

## 🗂️ Project Structure

```
silentguard/
├── home/
│   ├── ml_scanner.py          # ML-powered scam detection engine
│   ├── models.py              # 12 data models
│   ├── views.py               # 25+ view functions (upgraded)
│   ├── forms.py               # User, savings, investment forms
│   ├── templates/             # 24 HTML templates
│   │   ├── dashboard.html     # Fraud detection dashboard
│   │   ├── savings_dashboard.html  # Savings tracker with chart
│   │   ├── scan_result.html   # ML scan results
│   │   ├── profile.html       # User profile (editable)
│   │   ├── transactions.html  # Transaction history
│   │   ├── activity_log.html  # Security events
│   │   └── ...
│   ├── migrations/            # 12 database migrations
│   └── static/
├── silentguard/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── README.md
└── manage.py
```

---

## 🧠 ML Scam Detection Details

### How It Works

1. **Preprocessing**: Text is lowercased and tokenized
2. **Feature Extraction**: TF-IDF vectorization (1-2 grams, max 500 features)
3. **Classification**: Multinomial Naive Bayes trained on scam/safe samples
4. **Scoring**: Blended score (60% ML + 40% keyword) for robustness
5. **Fallback**: If scikit-learn unavailable, uses weighted keyword scoring

### Training Data
- **Scam samples**: 12 examples (lottery scams, pin requests, urgent unlocks)
- **Safe samples**: 10 examples (bank notifications, OTPs, bills)
- **Auto-retraining**: Model trains on-the-fly for each request (fast with small dataset)

### Keyword Weights
- **High-risk** (20-40 points): "send your pin", "you have won", "lottery", "jackpot"
- **Medium-risk** (5-10 points): "free", "win", "prize", "bonus", "claim"
- **Patterns**: Phone numbers in suspicious context (+15), URLs (+20)

### Trusted Senders
- Banks: ABSA, Stanbic, Centenary, DFCU, KCB, Equity
- Telcos: MTN, Airtel, UTL, Africell
- Toll-free: 0800 numbers

---

## 📊 Database Models

1. **UserProfile** — Custom user with account number, phone, location
2. **BankAccount** — Virtual bank account with balance
3. **Transaction** — All financial transactions
4. **SavingGoal** — User savings targets with progress tracking
5. **ScannedMessage** — SMS scan results with ML scores
6. **FraudReport** — User-submitted fraud reports
7. **NumberBlacklist** — Global blacklist of scammer numbers
8. **RiskyTransaction** — Flagged withdrawal attempts
9. **SuspiciousActivityLog** — Security events with geolocation
10. **InvestmentOption** — Available investment products
11. **EducationalContent** — Fraud prevention resources
12. **Feedback** — User feedback collection

---

## 🔐 Security Best Practices

- All sensitive views require authentication
- Passwords are hashed (Django's built-in PBKDF2)
- CSRF protection enabled
- Account locking mechanism
- Activity logging with IP geolocation
- Email notifications for critical events
- Rate limiting ready (add `@ratelimit` decorators as needed)

---

## 🚧 Production Deployment Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper email backend (not Gmail SMTP)
- [ ] Configure static files serving (WhiteNoise or CDN)
- [ ] Set strong `SECRET_KEY` (use environment variable)
- [ ] Enable HTTPS
- [ ] Set up Celery for async tasks (email, SMS)
- [ ] Configure proper logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Regular database backups
- [ ] Rate limiting on public endpoints

---

## 🎨 UI/UX Highlights

- **Color Scheme**: Dark red (#8B0000) and crimson (#DC143C)
- **Glass-morphism**: Frosted glass cards with backdrop blur
- **Responsive**: Mobile-friendly Bootstrap 5 design
- **Animations**: Smooth transitions and hover effects
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for spending visualization
- **Accessibility**: Semantic HTML, proper labels, ARIA attributes

---

## 📈 Future Enhancements

- [ ] Real-time SMS scanning via Africa's Talking webhook
- [ ] Push notifications for scam alerts
- [ ] Community-driven blacklist with voting
- [ ] Advanced ML models (LSTM, BERT for text classification)
- [ ] Multi-language support (Luganda, Swahili)
- [ ] Mobile app (React Native or Flutter)
- [ ] Integration with real banks via APIs
- [ ] Spending budgets and alerts
- [ ] Recurring savings automation
- [ ] Investment portfolio tracking
- [ ] Social features (share scam warnings)

---

## 🤝 Contributing

This is a hackathon project by GirlCoders in Uganda. Contributions welcome!

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License — feel free to use and modify.

---

## 👥 Credits

**Built by GirlCoders in Uganda**

Special thanks to:
- Django community
- scikit-learn team
- Bootstrap team
- Chart.js team
- Africa's Talking

---

## 📞 Support

For issues or questions, please open a GitHub issue or contact the team.

---

**Stay safe with SilentGuard! 🛡️**
