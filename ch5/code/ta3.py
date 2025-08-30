import sys
import os
from os.path import dirname, abspath
import shutil
from datetime import datetime
import customtkinter as tk
from tkinter import messagebox, filedialog, ttk, Listbox, Scrollbar
from PIL import Image
import re
import math

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from common.CTkSpinbox import CTkSpinbox


main_dir = "m_tiny_studium/logs/v3_controlled"
user_name = "maz"
log_file_name = f"{main_dir}/{user_name}/{user_name}_behavior_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
data_file_name = f"{main_dir}/{user_name}/{user_name}_form_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

event_types = {"2": "Key", "9": "FocusIn", "5": "ButtonRelease"}

uploaded_files = {}
selected_record_index = None
overall_feedback = ""

os.makedirs(f"{main_dir}/{user_name}",exist_ok=True)

def log_chk_state(event, bool_var, widget_name):
    # widget_name = widget_names.get(event.widget, "")
    newState = bool_var.get()
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"{widget_name} - {'Checked' if newState else 'Unchecked'}", event_time)


def log_event(event, widget_name, extra_info=None):
    # widget_name = widget_names.get(event.widget, "")
    event_type = event_types.get(event.type, "")
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if event.type == "2":  # Key
        log(f"{widget_name} - {event_type} - {event.keysym}", event_time)
    elif event.type == "9":  # FocusIn
        log(f"{widget_name} - {event_type}", event_time)
    elif event.type == "5":  # ButtonRelease
        log(
            f"{widget_name} - {event_type}{' - ' + extra_info if extra_info else ''}",
            event_time,
        )


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
        "q1": q1_spinbox.get(),
        "q2": q2_spinbox.get(),
        "q3": q3_spinbox.get(),
        "grade": grade_spinbox.get(),
        "feedback": get_feedback(),
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
        q1_spinbox.set(record["q1"])
        q2_spinbox.set(record["q2"])
        q3_spinbox.set(record["q3"])
        grade_spinbox.set(record["grade"])
        set_feedback(record["feedback"])
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
            f"Student ID: {record['student_id']} - Q1: {record['q1']} - Q2: {record['q2']} - Q3: {record['q3']} - Grade: {record['grade']} - Feedback: {' | '.join(record['feedback'])} - Mark for attention: {'Yes' if record['attention'] else 'No'} - File: {os.path.basename(record['file_path'])}",
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
    q1_spinbox.set(0)
    q2_spinbox.set(0)
    q3_spinbox.set(0)
    grade_spinbox.set(0)
    clear_feedback()
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
                f"{record['student_id'].strip()},{record['q1']},{record['q2']},{record['q3']},{record['grade']},{' | '.join(record['feedback'])},{'Yes' if record['attention'] else 'No'},{record['file_path']}\n"
            )


def get_feedback():
    feedback = []
    if feedback_var1.get() and feedback1_entry.get():
        feedback.append("SF1: " + feedback1_entry.get().strip() + " SF1.")
    if feedback_var2.get() and feedback2_entry.get():
        feedback.append("SF2: " + feedback2_entry.get().strip() + " SF2.")
    if feedback_var3.get() and feedback3_entry.get():
        feedback.append("SF3: " + feedback3_entry.get().strip() + " SF3.")
    if feedback_var4.get() and feedback4_entry.get():
        feedback.append("SF4: " + feedback4_entry.get().strip() + " SF4.")
    return feedback


def set_feedback(feedback):
    fb_text = " | ".join(feedback)
    feedback_var1.set("SF1: " in fb_text and " SF1." in fb_text)
    if feedback_var1.get():
        feedback1_entry.configure(state="normal")
        feedback1_entry.insert(0, extract_single_feedback(fb_text, "SF1"))

    feedback_var2.set("SF2: " in fb_text and " SF2." in fb_text)
    if feedback_var2.get():
        feedback2_entry.configure(state="normal")
        feedback2_entry.insert(0, extract_single_feedback(fb_text, "SF2"))

    feedback_var3.set("SF3: " in fb_text and " SF3." in fb_text)
    if feedback_var3.get():
        feedback3_entry.configure(state="normal")
        feedback3_entry.insert(0, extract_single_feedback(fb_text, "SF3"))

    feedback_var4.set("SF4: " in fb_text and " SF4." in fb_text)
    if feedback_var4.get():
        feedback4_entry.configure(state="normal")
        feedback4_entry.insert(0, extract_single_feedback(fb_text, "SF4"))


def extract_single_feedback(feedback, token):
    pattern = rf"{token}: (.*?) {token}\."
    match = re.search(pattern, feedback)
    if match:
        return match.group(1)
    else:
        return None


def clear_feedback():
    feedback_var1.set(False)
    feedback1_entry.delete(0, tk.END)
    feedback1_entry.configure(state="disabled")
    feedback_var2.set(False)
    feedback2_entry.delete(0, tk.END)
    feedback2_entry.configure(state="disabled")
    feedback_var3.set(False)
    feedback3_entry.delete(0, tk.END)
    feedback3_entry.configure(state="disabled")
    feedback_var4.set(False)
    feedback4_entry.delete(0, tk.END)
    feedback4_entry.configure(state="disabled")


root = tk.CTk()
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()
# x = math.floor(1.6 * screen_width)
# y = math.floor(0.1 * screen_height)
# root.geometry(f"950x720+{x}+{y}")

root.title("Tiny Studium")
root.resizable(False, False)
# root.iconbitmap("themes/ico/studium.ico")
root.iconbitmap("themes/ico/stu.svg")
tk.set_appearance_mode("dark")
tk.set_default_color_theme("themes/Cobalt.json")

# GUI elements
tk.CTkLabel(root, text="Student ID: ").grid(row=0, column=0, sticky="e")
student_id_entry = tk.CTkEntry(root, width=140)
student_id_entry.grid(row=0, column=1, columnspan=6, padx=10, pady=10, sticky="w")
student_id_entry.bind("<Key>", lambda event: log_event(event, "Student ID"))
student_id_entry.bind("<FocusIn>", lambda event: log_event(event, "Student ID"))


def create_spinbox(name, parent, row, column):
    spinbox = CTkSpinbox(parent, width=135)
    spinbox.grid(row=row, column=column, pady=10, sticky="w")
    spinbox.add_button.bind(
        "<ButtonRelease>", lambda event: log_event(event, name, spinbox.entry.get())
    )
    spinbox.subtract_button.bind(
        "<ButtonRelease>", lambda event: log_event(event, name, spinbox.entry.get())
    )
    spinbox.entry.bind("<Key>", lambda event: log_event(event, name))
    spinbox.entry.bind("<FocusIn>", lambda event: log_event(event, name))
    spinbox.set(0)
    return spinbox


tk.CTkLabel(root, text="Q1: ").grid(row=1, column=0, sticky="e")
q1_spinbox = create_spinbox("Q1", root, 1, 1)
tk.CTkLabel(root, text="Q2: ").grid(row=1, column=2, sticky="e")
q2_spinbox = create_spinbox("Q2", root, 1, 3)
tk.CTkLabel(root, text="Q3: ").grid(row=1, column=4, sticky="e")
q3_spinbox = create_spinbox("Q3", root, 1, 5)
tk.CTkLabel(root, text="Total grade: ").grid(row=2, column=0, sticky="e")
grade_spinbox = create_spinbox("Q4", root, 2, 1)

separator = ttk.Separator(root, orient="horizontal")
separator.grid(row=3, column=0, columnspan=7, sticky="nsew", pady=30, padx=150)

#############################################################
feedback_var1 = tk.BooleanVar()
feedback_var2 = tk.BooleanVar()
feedback_var3 = tk.BooleanVar()
feedback_var4 = tk.BooleanVar()


def toggle_textbox(var, textbox):
    if var.get():
        textbox.configure(state="normal")
    else:
        textbox.delete(0, tk.END)
        textbox.configure(state="disabled")


tk.CTkLabel(root, text="Student feedback: ").grid(row=4, column=0, sticky="e")
feedback1_entry = tk.CTkEntry(root, width=350, state="disabled")
feedback1_entry.grid(row=4, column=1, columnspan=3, padx=10, pady=10, sticky="w")
feedback1_entry.bind("<Key>", lambda event: log_event(event, "SF1 text"))
feedback1_entry.bind("<FocusIn>", lambda event: log_event(event, "SF1 text"))
sf1_check = tk.CTkCheckBox(
    root,
    text="Add feedback 1",
    variable=feedback_var1,
    command=lambda: toggle_textbox(feedback_var1, feedback1_entry),
)
sf1_check.grid(row=4, column=4, columnspan=2, pady=10, sticky="w")
sf1_check.bind(
    "<space>", lambda event: log_chk_state(event, feedback_var1, "Add feedback 1")
)
sf1_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, feedback_var1, "Add feedback 1")
)

feedback2_entry = tk.CTkEntry(root, width=350, state="disabled")
feedback2_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=10, sticky="w")
feedback2_entry.bind("<Key>", lambda event: log_event(event, "SF2 text"))
feedback2_entry.bind("<FocusIn>", lambda event: log_event(event, "SF2 text"))
sf2_check = tk.CTkCheckBox(
    root,
    text="Add feedback 2",
    variable=feedback_var2,
    command=lambda: toggle_textbox(feedback_var2, feedback2_entry),
)
sf2_check.grid(row=5, column=4, columnspan=2, pady=10, sticky="w")
sf2_check.bind(
    "<space>", lambda event: log_chk_state(event, feedback_var2, "Add feedback 2")
)
sf2_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, feedback_var2, "Add feedback 2")
)

feedback3_entry = tk.CTkEntry(root, width=350, state="disabled")
feedback3_entry.grid(row=6, column=1, columnspan=3, padx=10, pady=10, sticky="w")
feedback3_entry.bind("<Key>", lambda event: log_event(event, "SF3 text"))
feedback3_entry.bind("<FocusIn>", lambda event: log_event(event, "SF3 text"))
sf3_check = tk.CTkCheckBox(
    root,
    text="Add feedback 3",
    variable=feedback_var3,
    command=lambda: toggle_textbox(feedback_var3, feedback3_entry),
)
sf3_check.grid(row=6, column=4, columnspan=2, pady=10, sticky="w")
sf3_check.bind(
    "<space>", lambda event: log_chk_state(event, feedback_var3, "Add feedback 3")
)
sf3_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, feedback_var3, "Add feedback 3")
)

feedback4_entry = tk.CTkEntry(root, width=350, state="disabled")
feedback4_entry.grid(row=7, column=1, columnspan=3, padx=10, pady=10, sticky="w")
feedback4_entry.bind("<Key>", lambda event: log_event(event, "SF4 text"))
feedback4_entry.bind("<FocusIn>", lambda event: log_event(event, "SF4 text"))
sf4_check = tk.CTkCheckBox(
    root,
    text="Add feedback 4",
    variable=feedback_var4,
    command=lambda: toggle_textbox(feedback_var4, feedback4_entry),
)
sf4_check.grid(row=7, column=4, columnspan=2, pady=10, sticky="w")
sf4_check.bind(
    "<space>", lambda event: log_chk_state(event, feedback_var4, "Add feedback 4")
)
sf4_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, feedback_var4, "Add feedback 4")
)
####################################################################################

flag_var = tk.BooleanVar()
tk.CTkLabel(root, text="Mark for attention: ").grid(row=8, column=0, sticky="e")
flag_check = tk.CTkCheckBox(root, variable=flag_var, text="")
flag_check.grid(row=8, column=1, columnspan=7, padx=10, pady=10, sticky="w")
flag_check.bind(
    "<space>", lambda event: log_chk_state(event, flag_var, "Mark for attention")
)
flag_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, flag_var, "Mark for attention")
)

tk.CTkLabel(root, text="Additional doc (optional): ").grid(row=9, column=0, sticky="e")
file_path_label = tk.CTkLabel(
    root, text="Comments, docs, images related to the student"
)
file_path_label.grid(row=9, column=2, columnspan=5, sticky="nsew", padx=100, pady=10)

widget_names = {
    student_id_entry: "Student ID",
    q1_spinbox: "Q1",
    q2_spinbox: "Q2",
    q3_spinbox: "Q3",
    grade_spinbox: "Total grade",
    sf1_check: "Add feedback 1",
    sf2_check: "Add feedback 2",
    sf3_check: "Add feedback 3",
    sf4_check: "Add feedback 4",
    feedback1_entry: "Feedback 1",
    feedback2_entry: "Feedback 2",
    feedback3_entry: "Feedback 3",
    feedback4_entry: "Feedback 4",
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
upload_button.grid(row=9, column=1, sticky="w", padx=10, pady=10)

save_button = tk.CTkButton(
    root,
    text="Save current record",
    command=save_data,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/save.png"), size=(24, 24)),
    compound=tk.LEFT,
)
save_button.grid(row=10, column=2, columnspan=5, sticky="e", padx=100, pady=(40, 10))

separator1 = ttk.Separator(root, orient="horizontal")
separator1.grid(row=11, column=0, columnspan=7, sticky="nsew", pady=30)

view_button = tk.CTkButton(
    root,
    text="View already entered records",
    command=view_records,
    image=tk.CTkImage(Image.open("themes/ico/view.png"), size=(24, 24)),
    compound=tk.LEFT,
)
view_button.grid(row=12, column=0, sticky="w", padx=10, pady=10)

feedback_button = tk.CTkButton(
    root,
    text="Provide overall feedback to instructor",
    command=add_overall_feedback,
    image=tk.CTkImage(Image.open("themes/ico/feedback.png"), size=(24, 24)),
    compound=tk.LEFT,
)
feedback_button.grid(row=12, column=1, columnspan=3, sticky="w", padx=10, pady=10)

submit_button = tk.CTkButton(
    root,
    text="Submit all records",
    command=proceed_to_submit_records,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/all.png"), size=(24, 24)),
    compound=tk.LEFT,
)
submit_button.grid(row=12, column=4, columnspan=2, sticky="w", padx=10, pady=10)


log(f"Form - Started")
root.mainloop()
log(f"Form - Destroyed")
