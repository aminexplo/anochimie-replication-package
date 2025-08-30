import sys
import os
from os.path import dirname, abspath
import shutil
import re
from datetime import datetime
import customtkinter as tk
from tkinter import messagebox, filedialog, ttk, Listbox, Scrollbar
from tkinter.colorchooser import askcolor
from tkcalendar import DateEntry
from PIL import Image
import math

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from common.CTkSpinbox import CTkSpinbox


main_dir = "m_conference_registration/logs"
user_name = "maz"
log_file_name = f"{main_dir}/{user_name}/{user_name}_behavior_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
data_file_name = f"{main_dir}/{user_name}/{user_name}_form_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

event_types = {
    "2": "Key",
    "5": "ButtonRelease",
    "9": "FocusIn",
    "35": "DateEntrySelected",
}

uploaded_files = {}
selected_record_index = None
overall_feedback = ""

if not os.path.exists(f"{main_dir}/{user_name}"):
    os.makedirs(f"{main_dir}/{user_name}")


def log_chk_state(event, bool_var, widget_name):
    newState = bool_var.get()
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"{widget_name} - {'Checked' if newState else 'Unchecked'}", event_time)


def log_event(event, widget_name, extra_info=None):
    event_type = event_types.get(event.type, "")
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if event.type == "2":  # Key
        # {' - '+str(event.widget.get()) if widget_name in grades_widget_names else ''}
        log(
            f"{widget_name} - {event_type} - {event.keysym}",
            event_time,
        )
    elif event.type == "9":  # FocusIn
        log(f"{widget_name} - {event_type}", event_time)
    elif event.type == "5":  # ButtonRelease
        # selected_item = event.widget.get()
        log(f"{widget_name} - {event_type} - {extra_info}", event_time)
    elif event.type == "35":  # DateEntrySelected
        log(f"{widget_name} - {event_type} - {event.widget.get()}", event_time)


def log(text, log_time=None):
    if not log_time:
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file_name, "a") as log_file:
        log_file.write(f"{text} - {log_time}\n")


def save_data():
    participant_id = id_entry.get()
    participant_email = email_entry.get()
    log(
        f"Save clicked - ID: {'No ID' if not participant_id else participant_id.strip()}"
    )

    if not participant_id:
        log("Please enter an ID before saving a record.")
        messagebox.showwarning("Warning", "Please enter an ID before saving a record.")
        return

    if not meal_pref_var.get():
        log("Please choose a meal preference before saving a record.")
        messagebox.showwarning(
            "Warning", "Please choose a meal preference before saving a record."
        )
        return

    if not re.match(r"[^@]+@[^@]+\.[^@]+", participant_email):
        log("Please enter a valid Email address before saving a record.")
        messagebox.showwarning(
            "Warning", "Please enter a valid Email address before saving a record."
        )
        return

    global selected_record_index

    record = {
        "id": participant_id,
        "email": participant_email,
        "meal_preference": meal_pref_var.get(),
        "allergic": allergic_var.get(),
        "topic_of_interest": topics_var.get(),
        "website_rating": website_rating_slider.get(),
        "reminder_date": reminder_date_entry.get(),
        "previous_versions": prev_particip_spinbox.get(),
    }

    if selected_record_index is not None:
        records[selected_record_index] = record
        selected_record_index = None
    else:
        records.append(record)

    clear_entries()
    save_records_to_file()


records = []


def view_records():
    log("View records clicked")
    root.focus_set()
    record_window = tk.CTkToplevel(root)
    record_window.resizable(False, False)
    record_window.transient(root)
    record_window.lift()
    record_window.title("View Records")
    center_toplevel(record_window)

    def select_record():
        global selected_record_index
        selected_record_index = record_listbox.curselection()[0]
        record = records[selected_record_index]

        log(f"Select record clicked - ID: {record['id'].strip()}")

        id_entry.delete(0, tk.END)
        id_entry.insert(0, record["id"])
        email_entry.delete(0, tk.END)
        email_entry.insert(0, record["email"])

        meal_pref_var.set(record["meal_preference"])
        allergic_var.set(record["allergic"])
        topics_var.set(record["topic_of_interest"])

        website_rating_val = int(record["website_rating"])
        website_rating_slider.set(website_rating_val)
        website_rating_label.configure(text=website_rating_val)

        reminder_date_entry.set_date(record["reminder_date"])

        prev_particip_spinbox.set(record["previous_versions"])

        record_window.destroy()
        root.focus_set()

    record_listbox = Listbox(
        record_window,
        width=50,
        height=20,
        bg="#284a68",
        fg="#b4ccd8",
        font=("Roboto Condensed", 18),
    )

    v_scrollbar = Scrollbar(
        record_window, orient=tk.VERTICAL, command=record_listbox.yview
    )
    h_scrollbar = Scrollbar(
        record_window, orient=tk.HORIZONTAL, command=record_listbox.xview
    )
    record_listbox.config(
        yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
    )

    record_listbox.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
    h_scrollbar.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

    record_window.grid_rowconfigure(0, weight=1)
    record_window.grid_columnconfigure(0, weight=1)

    for record in records:
        record_listbox.insert(
            tk.END,
            f"ID: {record['id'].strip()} - Email: {record['email'].strip()} - Meal preference: {record['meal_preference']} - Allergic: {'Yes' if record['allergic'] else 'No'} - Topic of interest: {record['topic_of_interest'].strip()} - Website rating: {int(record['website_rating'])} - Reminder date: {record['reminder_date'].strip()} - Previously participated: {record['previous_versions']}",
        )

    select_button = tk.CTkButton(
        record_window,
        width=120,
        text="Select record",
        command=select_record,
        image=tk.CTkImage(Image.open("themes/ico/select.png"), size=(24, 24)),
        compound=tk.LEFT,
    )
    select_button.grid(row=2, column=0, pady=5, padx=10)


def center_toplevel(top_level):
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    top_level_width = 640
    top_level_height = 480

    center_x = root_x + (root_width // 2) - (top_level_width // 2)
    center_y = root_y + (root_height // 2) - (top_level_height // 2)

    top_level.geometry(f"{top_level_width}x{top_level_height}+{center_x}+{center_y}")


def add_overall_feedback():
    log("Add overall feedback clicked")

    def save_feedback():
        global overall_feedback
        overall_feedback = (
            email_text_area.get("1.0", "end-1c").replace("\r", "").replace("\n", " ")
        )
        log(f"Overall feedback saved: {overall_feedback}")
        messagebox.showinfo("Comment Saved", "Your comment has been saved.")
        email_window.destroy()
        root.focus_set()

    root.focus_set()
    email_window = tk.CTkToplevel(root)
    email_window.resizable(False, False)
    email_window.transient(root)
    email_window.lift()
    email_window.title("Add Overall Comment")
    center_toplevel(email_window)

    tk.CTkLabel(
        email_window,
        text="Overall comments for the registration team (optional): ",
    ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

    email_text_area = tk.CTkTextbox(email_window, height=370, width=610)
    email_text_area.grid(row=1, column=0, padx=10, pady=5)

    if overall_feedback:
        email_text_area.insert("1.0", overall_feedback)

    save_button = tk.CTkButton(
        email_window,
        width=120,
        text="Save comment",
        command=save_feedback,
        image=tk.CTkImage(Image.open("themes/ico/save.png"), size=(24, 24)),
        compound=tk.LEFT,
    )
    save_button.grid(row=2, column=0, padx=10, pady=5)

    email_window.mainloop()


def proceed_to_submit_records():
    log("Submit records clicked")

    if messagebox.askyesno(
        "Confirm Submission", "Are you sure you want to submit the records?"
    ):
        log("Submit and exit confirmed")
        with open(data_file_name, "a") as data_file:
            if overall_feedback:
                data_file.write(f"\nOverall feedback: {overall_feedback}\n")
        messagebox.showinfo("Success", "Thank you for your time and assistance.")
        root.destroy()
    else:
        log("Submission cancelled by user")


def clear_entries():
    id_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    meal_pref_var.set("")
    allergic_check.deselect()
    topics_var.set("")
    website_rating_slider.set(1)
    website_rating_label.configure(text="1")
    reminder_date_entry.set_date(datetime.now().date())
    prev_particip_spinbox.set(0)


def save_records_to_file():
    with open(data_file_name, "w") as data_file:
        write_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_file.write(f"---\n{write_time}\n---\n")
        for record in records:
            data_file.write(
                f"{record['id'].strip()},{record['email'].strip()},{record['meal_preference']},{'Yes' if record['allergic'] else 'No'},{record['topic_of_interest'].strip()},{int(record['website_rating'])},{record['reminder_date']},{record['previous_versions']}\n"
            )


root = tk.CTk()
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()
# x = math.floor(1.6 * screen_width)
# y = math.floor(0.1 * screen_height)
# root.geometry(f"950x500+{x}+{y}")

root.title("Conference Registration")
root.resizable(False, False)
root.iconbitmap("themes/ico/stu.svg")
tk.set_appearance_mode("dark")
tk.set_default_color_theme("themes/Cobalt.json")

# GUI elements
tk.CTkLabel(root, text="ID: ").grid(row=0, column=0, padx=10, pady=10, sticky="e")
id_entry = tk.CTkEntry(root, width=200)
id_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
id_entry.bind("<Key>", lambda event: log_event(event, "ID"))
id_entry.bind("<FocusIn>", lambda event: log_event(event, "ID"))

tk.CTkLabel(root, text="Email: ").grid(row=0, column=2, padx=10, pady=10, sticky="e")
email_entry = tk.CTkEntry(root, width=200)
email_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")
email_entry.bind("<Key>", lambda event: log_event(event, "Email"))
email_entry.bind("<FocusIn>", lambda event: log_event(event, "Email"))


def radiobutton_event():
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"Meal preference - Toggled - {meal_pref_var.get()}", event_time)


tk.CTkLabel(root, text="Meal preference: ").grid(
    row=1, column=0, padx=10, pady=10, sticky="e"
)
meal_pref_var = tk.StringVar()
rad_frame = tk.CTkFrame(root, border_width=0)
rad_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")
vegetarian_radio = tk.CTkRadioButton(
    rad_frame,
    text="Meat",
    command=radiobutton_event,
    variable=meal_pref_var,
    value="Meat",
)
vegetarian_radio.grid(row=0, column=0, padx=10, pady=10, sticky="w")
vegan_radio = tk.CTkRadioButton(
    rad_frame,
    text="Fish",
    command=radiobutton_event,
    variable=meal_pref_var,
    value="Fish",
)
vegan_radio.grid(row=1, column=0, padx=10, pady=10, sticky="w")
non_vegetarian_radio = tk.CTkRadioButton(
    rad_frame,
    text="Pasta (veg)",
    command=radiobutton_event,
    variable=meal_pref_var,
    value="Pasta (veg)",
)
non_vegetarian_radio.grid(row=2, column=0, padx=10, pady=10, sticky="w")


allergic_var = tk.BooleanVar()
allergic_check = tk.CTkCheckBox(root, variable=allergic_var, text="Allergic")
allergic_check.grid(row=1, column=3, padx=10, pady=10, sticky="w")
allergic_check.bind(
    "<space>", lambda event: log_chk_state(event, allergic_var, "Allergic")
)
allergic_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, allergic_var, "Allergic")
)


def combobox_callback(choice):
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"Topic of interest - ComboboxSelected - {choice}", event_time)


tk.CTkLabel(root, text="Topic of interest: ").grid(
    row=2, column=0, padx=10, pady=10, sticky="e"
)
topics_var = tk.StringVar()
topics_menu = tk.CTkComboBox(
    root,
    variable=topics_var,
    values=["MDE", "AI4SE", "SE4AI", "Empirical SE", "Software Testing"],
    command=combobox_callback,
    width=200,
)
topics_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
topics_menu.bind("<Key>", lambda event: log_event(event, "Topic of interest"))
topics_menu.bind("<FocusIn>", lambda event: log_event(event, "Topic of interest"))


def show_slider_val(value, label):
    label.configure(text=int(value))


tk.CTkLabel(root, text="Website rating: ").grid(
    row=2, column=2, padx=10, pady=10, sticky="e"
)
website_rating_slider = tk.CTkSlider(
    root,
    from_=1,
    to=5,
    number_of_steps=4,
    width=180,
    command=lambda value: show_slider_val(value, website_rating_label),
)
website_rating_slider.set(1)
website_rating_slider.grid(row=2, column=3, padx=(30, 0), pady=10, sticky="w")
website_rating_label = tk.CTkLabel(root, text="1")
website_rating_label.grid(row=2, column=3, padx=10, pady=10, sticky="w")
website_rating_slider.bind(
    "<ButtonRelease>",
    lambda event: log_event(event, "Website rating", website_rating_label.cget("text")),
)
website_rating_slider.bind("<Key>", lambda event: log_event(event, "Website rating"))
website_rating_slider.bind(
    "<FocusIn>", lambda event: log_event(event, "Website rating")
)


tk.CTkLabel(root, text="Next year reminder date: ").grid(
    row=3, column=2, padx=10, pady=10, sticky="e"
)
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "my.DateEntry",
    fieldbackground="#284a68",
    foreground="#b4ccd8",
    arrowcolor="#284a68",
    corner_radius="36",
)
reminder_date_entry = DateEntry(
    root, style="my.DateEntry", font=("Roboto Condensed", 18), locale="en_CA", width=19
)
reminder_date_entry.grid(row=3, column=3, padx=10, pady=10, sticky="w")
reminder_date_entry.bind(
    "<<DateEntrySelected>>", lambda event: log_event(event, "Next year reminder date")
)
reminder_date_entry.bind(
    "<FocusIn>", lambda event: log_event(event, "Next year reminder date")
)


tk.CTkLabel(root, text="# of prior versions participated: ").grid(
    row=3, column=0, sticky="w", padx=10, pady=5
)
prev_particip_spinbox = CTkSpinbox(root, width=185, min=0, max=10)
prev_particip_spinbox.grid(row=3, column=1, pady=10, padx=5, sticky="w")
prev_particip_spinbox.add_button.bind(
    "<ButtonRelease>",
    lambda event: log_event(
        event, "# of prior versions participated", prev_particip_spinbox.entry.get()
    ),
)
prev_particip_spinbox.subtract_button.bind(
    "<ButtonRelease>",
    lambda event: log_event(
        event, "# of prior versions participated", prev_particip_spinbox.entry.get()
    ),
)
prev_particip_spinbox.entry.bind(
    "<Key>", lambda event: log_event(event, "# of prior versions participated")
)
prev_particip_spinbox.entry.bind(
    "<FocusIn>", lambda event: log_event(event, "# of prior versions participated")
)
prev_particip_spinbox.set(0)


# Buttons
save_button = tk.CTkButton(
    root,
    text="Save current record",
    command=save_data,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/save.png"), size=(24, 24)),
    compound=tk.LEFT,
)
save_button.grid(row=4, column=3, sticky="w", padx=10, pady=(40, 10))

separator1 = ttk.Separator(root, orient="horizontal")
separator1.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=30)

view_button = tk.CTkButton(
    root,
    text="View already entered records",
    command=view_records,
    image=tk.CTkImage(Image.open("themes/ico/view.png"), size=(24, 24)),
    compound=tk.LEFT,
)
view_button.grid(row=6, column=0, columnspan=3, sticky="w", padx=10, pady=10)

feedback_button = tk.CTkButton(
    root,
    text="Provide overall comment to registration",
    command=add_overall_feedback,
    image=tk.CTkImage(Image.open("themes/ico/feedback.png"), size=(24, 24)),
    compound=tk.LEFT,
)
feedback_button.grid(row=6, column=1, columnspan=3, sticky="w", padx=(40, 0), pady=10)

submit_button = tk.CTkButton(
    root,
    text="Submit all records",
    command=proceed_to_submit_records,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/all.png"), size=(24, 24)),
    compound=tk.LEFT,
)
submit_button.grid(row=6, column=3, sticky="e", padx=(20, 5), pady=10)

log(f"Form - Started")
root.mainloop()
log(f"Form - Destroyed")
