import pywhatkit as kit
import schedule
import time
from datetime import datetime
import random
import pytz
from tkinter import *
from tkinter import messagebox, ttk
import logging
import os
import json
from PIL import ImageTk, Image
import pyautogui

class WhatsAppScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced WhatsApp Scheduler")
        self.root.geometry("800x600")
        self.setup_ui()
        self.load_contacts()
        self.setup_logging()
       
        # Start scheduler in background
        self.running = True
        self.check_scheduled_messages()

    def setup_logging(self):
        logging.basicConfig(
            filename='whatsapp_scheduler.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_ui(self):
        # Style configuration
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', padding=6, font=('Helvetica', 10))
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
       
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
       
        # Left panel - Message composer
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
       
        # Right panel - Scheduled messages
        right_frame = ttk.Frame(main_frame, width=400)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
       
        # Recipient selection
        ttk.Label(left_frame, text="Recipient(s):").pack(anchor=W, pady=(0, 5))
        self.recipient_var = StringVar()
        self.contact_combobox = ttk.Combobox(left_frame, textvariable=self.recipient_var)
        self.contact_combobox.pack(fill=X, pady=(0, 10))
       
        # Add contact button
        ttk.Button(left_frame, text="Add New Contact", command=self.add_contact_dialog).pack(pady=(0, 10))
       
        # Message type selection
        ttk.Label(left_frame, text="Message Type:").pack(anchor=W, pady=(0, 5))
        self.message_type = StringVar(value="text")
        ttk.Radiobutton(left_frame, text="Text", variable=self.message_type, value="text").pack(anchor=W)
        ttk.Radiobutton(left_frame, text="Image", variable=self.message_type, value="image").pack(anchor=W)
       
        # Message content
        self.text_frame = ttk.Frame(left_frame)
        self.text_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
        ttk.Label(self.text_frame, text="Message:").pack(anchor=W, pady=(0, 5))
        self.message_text = Text(self.text_frame, height=8, wrap=WORD)
        self.message_text.pack(fill=BOTH, expand=True)
       
        # Scheduled time
        ttk.Label(left_frame, text="Scheduled Time:").pack(anchor=W, pady=(10, 5))
        time_frame = ttk.Frame(left_frame)
        time_frame.pack(fill=X, pady=(0, 10))
       
        self.hour_var = StringVar(value="12")
        self.minute_var = StringVar(value="00")
       
        ttk.Label(time_frame, text="Hour:").pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(time_frame, from_=0, to=23, width=3, textvariable=self.hour_var,
                   format="%02.0f").pack(side=LEFT, padx=(0, 10))
       
        ttk.Label(time_frame, text="Minute:").pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(time_frame, from_=0, to=59, width=3, textvariable=self.minute_var,
                   format="%02.0f").pack(side=LEFT)
       
        # Recurrence
        ttk.Label(left_frame, text="Recurrence:").pack(anchor=W, pady=(10, 5))
        self.recurrence_var = StringVar(value="once")
        ttk.Radiobutton(left_frame, text="Once", variable=self.recurrence_var, value="once").pack(anchor=W)
        ttk.Radiobutton(left_frame, text="Daily", variable=self.recurrence_var, value="daily").pack(anchor=W)
        ttk.Radiobutton(left_frame, text="Weekly", variable=self.recurrence_var, value="weekly").pack(anchor=W)
       
        # Schedule button
        ttk.Button(left_frame, text="Schedule Message", command=self.schedule_message).pack(pady=20)
       
        # Scheduled messages list
        ttk.Label(right_frame, text="Scheduled Messages").pack()
        self.messages_tree = ttk.Treeview(right_frame, columns=("time", "recipient", "message", "recurrence"), show="headings")
        self.messages_tree.heading("time", text="Time")
        self.messages_tree.heading("recipient", text="Recipient")
        self.messages_tree.heading("message", text="Message Preview")
        self.messages_tree.heading("recurrence", text="Recurrence")
        self.messages_tree.column("time", width=100)
        self.messages_tree.column("recipient", width=100)
        self.messages_tree.column("message", width=150)
        self.messages_tree.column("recurrence", width=80)
        self.messages_tree.pack(fill=BOTH, expand=True, pady=(5, 0))
       
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.messages_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.messages_tree.configure(yscrollcommand=scrollbar.set)
       
        # Delete button
        ttk.Button(right_frame, text="Delete Selected", command=self.delete_scheduled).pack(pady=10)
       
        # Image selection (hidden by default)
        self.image_frame = ttk.Frame(left_frame)
        ttk.Label(self.image_frame, text="Image Path:").pack(anchor=W, pady=(0, 5))
        self.image_path_var = StringVar()
        ttk.Entry(self.image_frame, textvariable=self.image_path_var, state='readonly').pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Button(self.image_frame, text="Browse", command=self.browse_image).pack(side=RIGHT)
       
        # Show/hide elements based on message type
        self.message_type.trace_add('write', self.toggle_message_type)
       
        # Sample messages
        self.sample_messages = [
            "Hello! How are you?",
            "Reminder: Our meeting at 3 PM today",
            "Don't forget to complete the task",
            "Happy birthday! 🎉",
            "Just checking in on you"
        ]
        ttk.Button(left_frame, text="Insert Sample Message", command=self.insert_sample_message).pack(pady=5)

    def toggle_message_type(self, *args):
        if self.message_type.get() == "text":
            self.text_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
            self.image_frame.pack_forget()
        else:
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=X, pady=(10, 0))

    def browse_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image_path_var.set(file_path)

    def insert_sample_message(self):
        self.message_text.delete("1.0", END)
        self.message_text.insert("1.0", random.choice(self.sample_messages))

    def load_contacts(self):
        try:
            if os.path.exists("contacts.json"):
                with open("contacts.json", "r") as f:
                    contacts = json.load(f)
                    self.contact_combobox['values'] = contacts
        except Exception as e:
            logging.error(f"Error loading contacts: {e}")

    def save_contacts(self, contacts):
        try:
            with open("contacts.json", "w") as f:
                json.dump(contacts, f)
        except Exception as e:
            logging.error(f"Error saving contacts: {e}")

    def add_contact_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("Add New Contact")
        dialog.geometry("300x150")
       
        ttk.Label(dialog, text="Phone Number (with country code):").pack(pady=(10, 5))
        phone_entry = ttk.Entry(dialog)
        phone_entry.pack(fill=X, padx=10, pady=5)
       
        def add_contact():
            phone = phone_entry.get()
            if phone:
                current_contacts = list(self.contact_combobox['values'])
                if phone not in current_contacts:
                    current_contacts.append(phone)
                    self.contact_combobox['values'] = current_contacts
                    self.recipient_var.set(phone)
                    self.save_contacts(current_contacts)
                dialog.destroy()
       
        ttk.Button(dialog, text="Add", command=add_contact).pack(pady=10)

    def schedule_message(self):
        recipient = self.recipient_var.get()
        message_type = self.message_type.get()
        recurrence = self.recurrence_var.get()
       
        if not recipient:
            messagebox.showerror("Error", "Please select a recipient")
            return
           
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
           
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time")
               
            # Format time for display
            display_time = f"{hour:02d}:{minute:02d}"
           
            if message_type == "text":
                message = self.message_text.get("1.0", END).strip()
                if not message:
                    messagebox.showerror("Error", "Please enter a message")
                    return
               
                # Add to treeview
                self.messages_tree.insert("", "end", values=(display_time, recipient, message[:30] + ("..." if len(message) > 30 else ""), recurrence))
               
                # Schedule the message
                if recurrence == "once":
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.send_whatsapp_message, recipient, message).tag(f"{recipient}_{display_time}")
                elif recurrence == "daily":
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.send_whatsapp_message, recipient, message).tag(f"{recipient}_{display_time}")
                elif recurrence == "weekly":
                    schedule.every().monday.at(f"{hour:02d}:{minute:02d}").do(self.send_whatsapp_message, recipient, message).tag(f"{recipient}_{display_time}")
               
                logging.info(f"Scheduled message to {recipient} at {display_time} ({recurrence})")
               
            elif message_type == "image":
                image_path = self.image_path_var.get()
                if not image_path:
                    messagebox.showerror("Error", "Please select an image")
                    return
                   
                caption = self.message_text.get("1.0", END).strip()
               
                # Add to treeview
                self.messages_tree.insert("", "end", values=(display_time, recipient, f"Image: {os.path.basename(image_path)}", recurrence))
               
                # Schedule the message
                if recurrence == "once":
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.send_whatsapp_image, recipient, image_path, caption).tag(f"{recipient}_{display_time}")
                elif recurrence == "daily":
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.send_whatsapp_image, recipient, image_path, caption).tag(f"{recipient}_{display_time}")
                elif recurrence == "weekly":
                    schedule.every().monday.at(f"{hour:02d}:{minute:02d}").do(self.send_whatsapp_image, recipient, image_path, caption).tag(f"{recipient}_{display_time}")
               
                logging.info(f"Scheduled image to {recipient} at {display_time} ({recurrence})")
           
            messagebox.showinfo("Success", "Message scheduled successfully!")
           
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid time (HH:MM)")
        except Exception as e:
            logging.error(f"Error scheduling message: {e}")
            messagebox.showerror("Error", f"Failed to schedule message: {str(e)}")

    def send_whatsapp_message(self, phone, message):
        try:
            # Ensure phone number starts with '+' and has country code
            if not phone.startswith('+'):
                messagebox.showerror("Error", "Phone number must include country code and start with '+', e.g., +91878957845")
                logging.error(f"Country Code Missing in Phone Number: {phone}")
                return
            now = datetime.now()
            kit.sendwhatmsg(phone, message, now.hour, now.minute + 1, wait_time=30, tab_close=False)
            # Wait a bit longer to ensure message is typed
            time.sleep(35)
            pyautogui.press('enter')
            logging.info(f"Message sent to {phone}")
            messagebox.showinfo("Success", f"Message sent to {phone}")
        except Exception as e:
            logging.error(f"Error sending message to {phone}: {e}")
            # Retry after 5 minutes
            schedule.every(5).minutes.do(self.send_whatsapp_message, phone, message)

    def send_whatsapp_image(self, phone, image_path, caption=""):
        try:
            # Ensure phone number starts with '+' and has country code
            if not phone.startswith('+'):
                messagebox.showerror("Error", "Phone number must include country code and start with '+', e.g., +91878957845")
                logging.error(f"Country Code Missing in Phone Number: {phone}")
                return
            if not hasattr(kit, "sendwhats_image"):
                messagebox.showerror("Error", "Your pywhatkit version does not support sending images. Please install pywhatkit==5.4")
                logging.error("sendwhats_image not found in pywhatkit")
                return
            kit.sendwhats_image(phone, image_path, caption, 30, False)
            time.sleep(35)
            pyautogui.press('enter')
            logging.info(f"Image sent to {phone}")
            messagebox.showinfo("Success", f"Image sent to {phone}")
        except Exception as e:
            logging.error(f"Error sending image to {phone}: {e}")
            # Retry after 5 minutes
            schedule.every(5).minutes.do(self.send_whatsapp_image, phone, image_path, caption)

    def delete_scheduled(self):
        selected_item = self.messages_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a message to delete")
            return
           
        item = self.messages_tree.item(selected_item[0])
        time_str = item['values'][0]
        recipient = item['values'][1]
       
        # Remove from schedule
        schedule.clear(f"{recipient}_{time_str}")
       
        # Remove from treeview
        self.messages_tree.delete(selected_item[0])
       
        logging.info(f"Deleted scheduled message to {recipient} at {time_str}")

    def check_scheduled_messages(self):
        if self.running:
            schedule.run_pending()
        self.root.after(1000, self.check_scheduled_messages)

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = WhatsAppScheduler(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
