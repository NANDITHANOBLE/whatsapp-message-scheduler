# 💬 WhatsApp Message Scheduler

![Python](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

A simple Python GUI app to schedule WhatsApp messages (text or images) using `pywhatkit`, `Tkinter`, and local JSON storage. It allows saving favorite contacts, auto-scheduling messages, and supports both text and image-based WhatsApp messages.

---

## ✨ Features

* 📩 Send **Text or Image** messages
* 🕒 Schedule messages at **specific time**
* 💾 Store and select **frequent contacts**
* 💻 **Simple GUI** interface (Tkinter)
* 📦 Uses **pywhatkit** and **Pillow** for messaging/image

---

## 🖥️ GUI Interface Preview

![App Screenshot](whatsapp%20message.png)

> *(This shows the GUI interface of the WhatsApp Scheduler in action!)*

---

## ▶️ Demo (Step-by-step)

1. Open the app
2. Select/Add recipient (e.g., +919876543210)
3. Choose "Text" or "Image"
4. Write your message or pick an image
5. Set time (e.g., 14:30)
6. Click "Schedule"
7. Done! WhatsApp Web will send your message at the scheduled time

---

## 📂 Folder Structure

```
whatsapp-scheduler/
├── contacts.json
├── main.py
├── PyWhatKit_DB.txt
├── README.md
├── whatsapp message.png
├── whatsapp_scheduler.py
```

---

## 🛠️ Requirements

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

### `requirements.txt`

```txt
pywhatkit==5.4
schedule
pyautogui
Pillow
```

---

## 🧠 How It Works

* Uses `pywhatkit.sendwhatmsg()` for sending messages at scheduled time.
* Saves contacts in a local `contacts.json` file.
* Opens WhatsApp Web in browser automatically.
* Uses `schedule` module to schedule sending.

---

## 🚀 Running the App

```bash
python whatsapp_scheduler.py
```

---

## 🔐 LICENSE

This project is licensed under the MIT License.

---

## 🙌 Contributions

Contributions are welcome. Feel free to submit a PR or raise an issue.

---

## 🧾 TODO / Improvements

* Add support for recurring messages (e.g., daily reminder)
* Export/import contacts
* Convert to .exe using `pyinstaller`
* Add sound/vibration notification

---

## 📄 .gitignore (Recommended)

```gitignore
__pycache__/
*.pyc
*.log
*.db
.env
```

---

## 💡 Tips

* Make sure you are logged in to WhatsApp Web.
* Don't close the browser until message is sent.

---

## 📽️ Optional Demo GIF

If you want, record a short demo and place it in `assets/demo.gif`:

```markdown
![Demo](assets/demo.gif)
```

---

Made with ❤️ in Python
