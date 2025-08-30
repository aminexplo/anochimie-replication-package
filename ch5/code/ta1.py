import os
import shutil
from datetime import datetime
import customtkinter as tk
from tkinter import messagebox, filedialog, ttk, Listbox, Scrollbar
from PIL import Image
import math

main_dir = "m_tiny_studium/logs/v1_open"
user_name = "maz"
log_file_name = f"{main_dir}/{user_name}/{user_name}_behavior_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
data_file_name = f"{main_dir}/{user_name}/{user_name}_form_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

event_types = {"2": "Key", "9": "FocusIn"}

uploaded_files = {}
selected_record_index = None
overall_feedback = ""

os.makedirs(f"{main_dir}/{user_name}",exist_ok=True)

def log_chk_state(bool_var):
    newState = bool_var.get()
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"Mark for attention - {'Checked' if newState else 'Unchecked'}", event_time)


def log_event(event, widget_name):
    # widget_name = widget_names.get(event.widget, "")
    event_type = event_types.get(event.type, "")
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if event.type == "2":  # Key
        log(f"{widget_name} - {event_type} - {event.keysym}", event_time)
    elif event.type == "9":  # FocusIn
        log(f"{widget_name} - {event_type}", event_time)


def log(text, log_time=None):
    if not log_time:
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file_name, "a") as log_file:
        log_file.write(f"{text} - {log_time}\n")


def save_data():
    student_id = student_id_entry.get()
    log(f"Save clicked - ID: {'No ID' if not student_id else student_id.strip()}")

    if not student_id:
        log("Please enter a Student ID before saving a record.")
        messagebox.showwarning(
            "Warning", "Please enter a Student ID before saving a record."
        )
        return

    global selected_record_index

    record = {
        "student_id": student_id,
        "q1": q1_entry.get(),
        "q2": q2_entry.get(),
        "q3": q3_entry.get(),
        "grade": grade_entry.get(),
        "feedback": feedback_text.get("1.0", "end-1c"),
        "attention": flag_var.get(),
        "file_path": uploaded_files.get(student_id, ""),
    }

    if selected_record_index is not None:
        records[selected_record_index] = record
        selected_record_index = None
    else:
        records.append(record)

    clear_entries()
    save_records_to_file()


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

        log(f"Select record clicked - ID: {record['student_id'].strip()}")

        student_id_entry.delete(0, tk.END)
        student_id_entry.insert(0, record["student_id"])
        q1_entry.delete(0, tk.END)
        q1_entry.insert(0, record["q1"])
        q2_entry.delete(0, tk.END)
        q2_entry.insert(0, record["q2"])
        q3_entry.delete(0, tk.END)
        q3_entry.insert(0, record["q3"])
        grade_entry.delete(0, tk.END)
        grade_entry.insert(0, record["grade"])
        feedback_text.delete("1.0", tk.END)
        feedback_text.insert("1.0", record["feedback"])
        flag_var.set(record["attention"])

        if record["file_path"]:
            file_path_label.configure(
                text=f"File: {os.path.basename(record['file_path'])}"
            )

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
            f"Student ID: {record['student_id']} - Q1: {record['q1']} - Q2: {record['q2']} - Q3: {record['q3']} - Grade: {record['grade']} - Feedback: {record['feedback']} - Mark for attention: {'Yes' if record['attention'] else 'No'} - File: {os.path.basename(record['file_path'])}",
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
        messagebox.showinfo("Feedback Saved", "Your feedback has been saved.")
        email_window.destroy()
        root.focus_set()

    root.focus_set()
    email_window = tk.CTkToplevel(root)
    email_window.resizable(False, False)
    email_window.transient(root)
    email_window.lift()
    email_window.title("Add Overall Feedback")
    center_toplevel(email_window)

    tk.CTkLabel(
        email_window,
        text="Overall feedback and comments for the instructor (optional): ",
    ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

    email_text_area = tk.CTkTextbox(email_window, height=370, width=610)
    email_text_area.grid(row=1, column=0, padx=10, pady=5)

    if overall_feedback:
        email_text_area.insert("1.0", overall_feedback)

    save_button = tk.CTkButton(
        email_window,
        width=120,
        text="Save feedback",
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
    student_id_entry.delete(0, tk.END)
    q1_entry.delete(0, tk.END)
    q2_entry.delete(0, tk.END)
    q3_entry.delete(0, tk.END)
    grade_entry.delete(0, tk.END)
    feedback_text.delete("1.0", tk.END)
    flag_check.deselect()
    file_path_label.configure(text="Comments, docs, images related to the student")


def upload_file():
    log("Upload file clicked")
    root.focus_set()
    file_path = filedialog.askopenfilename()
    if file_path:
        student_id = student_id_entry.get()
        if not student_id:
            log("Please enter a Student ID before uploading a file.")
            messagebox.showwarning(
                "Warning", "Please enter a Student ID before uploading a file."
            )
            return
        new_file_name = f"{main_dir}/{user_name}/{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(file_path)}"
        shutil.copy(file_path, new_file_name)
        uploaded_files[student_id] = new_file_name
        log(f"File uploaded for {student_id}: {new_file_name}")
        messagebox.showinfo("File Upload", f"File uploaded: {new_file_name}")
        file_path_label.configure(text=f"File: {os.path.basename(new_file_name)}")
        root.focus_set()


def save_records_to_file():
    with open(data_file_name, "w") as data_file:
        write_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_file.write(f"---\n{write_time}\n---\n")
        for record in records:
            data_file.write(
                f"{record['student_id'].strip()},{record['q1'].strip()},{record['q2'].strip()},{record['q3'].strip()},{record['grade'].strip()},{record['feedback'].strip()},{'Yes' if record['attention'] else 'No'},{record['file_path']}\n"
            )


root = tk.CTk()
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()
# x = math.floor(1.6 * screen_width)
# y = math.floor(0.1 * screen_height)
# root.geometry(f"895x600+{x}+{y}")

root.title("Tiny Studium")
root.resizable(False, False)
# root.iconbitmap("themes/ico/studium.ico")
root.iconbitmap("themes/ico/stu.svg")
tk.set_appearance_mode("dark")
tk.set_default_color_theme("themes/Cobalt.json")


# GUI elements
tk.CTkLabel(root, text="Student ID: ").grid(row=0, column=0, sticky="e")
student_id_entry = tk.CTkEntry(root, width=120)
student_id_entry.grid(row=0, column=1, columnspan=7, padx=10, pady=10, sticky="w")
student_id_entry.bind("<Key>", lambda event: log_event(event, "Student ID"))
student_id_entry.bind("<FocusIn>", lambda event: log_event(event, "Student ID"))

tk.CTkLabel(root, text="Q1: ").grid(row=1, column=0, sticky="e")
q1_entry = tk.CTkEntry(root, width=60)
q1_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
q1_entry.bind("<Key>", lambda event: log_event(event, "Q1"))
q1_entry.bind("<FocusIn>", lambda event: log_event(event, "Q1"))

tk.CTkLabel(root, text="Q2: ").grid(row=1, column=2, sticky="e")
q2_entry = tk.CTkEntry(root, width=60)
q2_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
q2_entry.bind("<Key>", lambda event: log_event(event, "Q2"))
q2_entry.bind("<FocusIn>", lambda event: log_event(event, "Q2"))

tk.CTkLabel(root, text="Q3: ").grid(row=1, column=4, sticky="e")
q3_entry = tk.CTkEntry(root, width=60)
q3_entry.grid(row=1, column=5, padx=10, pady=10, sticky="w")
q3_entry.bind("<Key>", lambda event: log_event(event, "Q3"))
q3_entry.bind("<FocusIn>", lambda event: log_event(event, "Q3"))

tk.CTkLabel(root, text="Total grade: ").grid(row=1, column=6, sticky="e")
grade_entry = tk.CTkEntry(root, width=60)
grade_entry.grid(row=1, column=7, padx=10, pady=10, sticky="w")
grade_entry.bind("<Key>", lambda event: log_event(event, "Total grade"))
grade_entry.bind("<FocusIn>", lambda event: log_event(event, "Total grade"))

separator = ttk.Separator(root, orient="horizontal")
separator.grid(row=2, column=0, columnspan=8, sticky="nsew", pady=30, padx=100)

tk.CTkLabel(root, text="Student feedback: ").grid(row=3, column=0, sticky="e")
feedback_text = tk.CTkTextbox(root, height=100, width=450)
feedback_text.grid(row=3, column=1, columnspan=7, padx=10, pady=10, sticky="w")
feedback_text.bind("<Key>", lambda event: log_event(event, "Student feedback"))
feedback_text.bind("<FocusIn>", lambda event: log_event(event, "Student feedback"))

tk.CTkLabel(root, text="Mark for attention: ").grid(row=4, column=0, sticky="e")
flag_var = tk.BooleanVar()
flag_check = tk.CTkCheckBox(root, variable=flag_var, text="")
flag_check.grid(row=4, column=1, columnspan=7, padx=10, pady=10, sticky="w")
flag_check.bind("<space>", lambda event: log_chk_state(flag_var))
flag_check.bind("<Button-1>", lambda event: log_chk_state(flag_var))

tk.CTkLabel(root, text="Additional doc (optional): ").grid(row=5, column=0, sticky="e")
file_path_label = tk.CTkLabel(
    root, text="Comments, docs, images related to the student"
)
file_path_label.grid(row=5, column=1, columnspan=7, sticky="e", padx=100, pady=10)

widget_names = {
    student_id_entry: "Student ID",
    q1_entry: "Q1",
    q2_entry: "Q2",
    q3_entry: "Q3",
    grade_entry: "Total grade",
    feedback_text: "Student feedback",
    flag_check: "Mark for attention",
}

records = []

# Buttons
upload_button = tk.CTkButton(
    root,
    text="Upload file",
    command=upload_file,
    image=tk.CTkImage(Image.open("themes/ico/upload.png"), size=(24, 24)),
    compound=tk.LEFT,
)
upload_button.grid(row=5, column=1, columnspan=7, sticky="w", padx=10, pady=10)

save_button = tk.CTkButton(
    root,
    text="Save current record",
    command=save_data,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/save.png"), size=(24, 24)),
    compound=tk.LEFT,
)
save_button.grid(row=6, column=1, columnspan=7, sticky="e", padx=100, pady=(40, 10))

separator1 = ttk.Separator(root, orient="horizontal")
separator1.grid(row=7, column=0, columnspan=8, sticky="nsew", pady=30)

view_button = tk.CTkButton(
    root,
    text="View already entered records",
    command=view_records,
    image=tk.CTkImage(Image.open("themes/ico/view.png"), size=(24, 24)),
    compound=tk.LEFT,
)
view_button.grid(row=8, column=0, sticky="w", padx=10, pady=10)

feedback_button = tk.CTkButton(
    root,
    text="Provide overall feedback to instructor",
    command=add_overall_feedback,
    image=tk.CTkImage(Image.open("themes/ico/feedback.png"), size=(24, 24)),
    compound=tk.LEFT,
)
feedback_button.grid(row=8, column=1, columnspan=6, sticky="w", padx=10, pady=10)

submit_button = tk.CTkButton(
    root,
    text="Submit all records",
    command=proceed_to_submit_records,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/all.png"), size=(24, 24)),
    compound=tk.LEFT,
)
submit_button.grid(row=8, column=7, sticky="e", padx=10, pady=10)

log(f"Form - Started")
root.mainloop()
log(f"Form - Destroyed")
