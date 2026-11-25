# מערכת הזמנת ארוחות – מודול ניהול תפריט

האפליקציה היא חלק קטן ורספונסיבי של המערכת. היא מפעילה את UC024–UC026 מול Microsoft SQL Server בעזרת הטבלאות `Restaurant` ו־`MenuItem`.

חשוב: אין לפתוח את `index.html` ישירות. האפליקציה עובדת דרך שרת FastAPI מקומי, ולכן צריך להפעיל את Uvicorn ולפתוח את הכתובת שמופיעה בהוראות. זה אינו קישור ציבורי באינטרנט.

## דרישות מוקדמות

- Windows עם Python 3.12
- Microsoft SQL Server ו־SQL Server Management Studio
- Microsoft ODBC Driver 18 for SQL Server

## הפעלה אחרי ההתקנה

פתחו את תיקיית **קוד האפליקציה** בסייר הקבצים, הקלידו `powershell` בשורת הכתובת ולחצו Enter. בחלון שנפתח הריצו את פקודת ההפעלה.

```powershell
& (Join-Path $PWD.Path '.venv312\Scripts\python.exe') -m uvicorn main:app --reload
```

כשתופיע ההודעה `Application startup complete`, פתחו את [האתר המקומי](http://127.0.0.1:8000). השאירו את חלון PowerShell פתוח בזמן השימוש. לעצירת השרת לחצו `Ctrl+C`.

## התקנה ראשונה

### 1. יצירת מסד הנתונים והטבלאות

בהתקנה חדשה, פתחו ב־SSMS את `sql/01_create_database.sql` ולחצו Execute. הסקריפט יוצר את `MealOrderingDemo` אם הוא חסר. אם הטבלאות כבר קיימות, הרצה חוזרת מוחקת אותן ואת הנתונים שבהן. דלגו על השלב אם הטבלאות כבר מוכנות.

### 2. יצירת סביבת Python

פתחו PowerShell בתיקיית **קוד האפליקציה** כפי שמתואר בסעיף ההפעלה. הפקודה יוצרת את התיקייה `.venv312` עבור ספריות הפרויקט.

```powershell
py -3.12 -m venv .venv312
```

### 3. התקנת הספריות

הפקודה מתקינה בסביבה החדשה את הספריות שמופיעות ב־`requirements.txt`.

```powershell
& (Join-Path $PWD.Path '.venv312\Scripts\python.exe') -m pip install -r requirements.txt
```

### 4. הגדרת החיבור למסד

צרו את `.env` מתוך התבנית. אם הקובץ כבר קיים, הפקודה תשאיר את ההגדרות הקיימות.

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
```

פתחו את קובץ ההגדרות לעריכה.

```powershell
notepad .env
```

בשורה `DB_SERVER`, החליפו את `localhost` בשם השרת שמופיע בשדה `Server name` בחלון החיבור של SSMS ושמרו. ברירת המחדל היא הזדהות Windows.

### 5. טעינת נתוני דוגמה

אם שתי הטבלאות ריקות, הריצו את הסקריפט כדי להוסיף חמש מסעדות וחמש מנות. בסיום תופיע ההודעה `Database connection succeeded.` ואחריה הרשומות שנוספו.

```powershell
& (Join-Path $PWD.Path '.venv312\Scripts\python.exe') .\seed_demo_data.py
```

עכשיו אפשר להפעיל את האתר לפי סעיף **הפעלה אחרי ההתקנה**.

## מבנה הפרויקט

| קובץ או תיקייה | תפקיד |
| --- | --- |
| `main.py` | ממשק ה־API והגשת האתר |
| `database.py` | הגדרת החיבור ל־SQL Server |
| `static/` | קובצי הממשק בדפדפן |
| `sql/` | יצירת הטבלאות ואימות שינויים במסד |
| `seed_demo_data.py` | טעינת מסעדות ומנות לדוגמה |
| `requirements.txt` | ספריות Python הנדרשות לפרויקט |
| `.env.example` | תבנית הגדרות החיבור |
| `tests.py` | בדיקות אוטומטיות לפרויקט |

## תרחישי השימוש

- UC024 – הוספת מנה חדשה לתפריט: הפעולה מתבצעת באמצעות `POST /api/menu-items`.
- UC025 – עריכת המחיר והתיאור של מנה קיימת: הפעולה מתבצעת באמצעות `PUT /api/menu-items/{id}`.
- UC026 – סימון מנה כחסרה במלאי: הפעולה מתבצעת באמצעות `PATCH /api/menu-items/{id}/stock`. אותו כפתור מחזיר את המנה לזמינה כשצריך.

## אימות השינוי ב־SQL Server

לאחר פעולה בממשק, הריצו ב־SSMS את `sql/02_verify_changes.sql`. הרשומה החדשה או המעודכנת צריכה להופיע בתוצאה.

## הערת אבטחה

אין להגיש את קובץ `.env` האישי אם הוא כולל שם משתמש או סיסמה. מגישים רק את `.env.example`.
