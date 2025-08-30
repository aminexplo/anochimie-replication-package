import os
import shutil
from datetime import datetime
import customtkinter as tk
from tkinter import messagebox, filedialog, ttk, Listbox, Scrollbar
from PIL import Image
import math

main_dir = "m_tiny_studium/logs/v2_predetermined"
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
        "q1": q1_scale.get(),
        "q2": q2_scale.get(),
        "q3": q3_scale.get(),
        "grade": grade_scale.get(),
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
        q1_val = int(record["q1"])
        q1_scale.set(q1_val)
        q1_label.configure(text=q1_val)
        q2_val = int(record["q2"])
        q2_scale.set(q2_val)
        q2_label.configure(text=q2_val)
        q3_val = int(record["q3"])
        q3_scale.set(q3_val)
        q3_label.configure(text=q3_val)
        grade_val = int(record["grade"])
        grade_scale.set(grade_val)
        grade_label.configure(text=grade_val)
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
            f"Student ID: {record['student_id']} - Q1: {int(record['q1'])} - Q2: {int(record['q2'])} - Q3: {int(record['q3'])} - Grade: {int(record['grade'])} - Feedback: {' | '.join(record['feedback'])} - Mark for attention: {'Yes' if record['attention'] else 'No'} - File: {os.path.basename(record['file_path'])}",
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
    q1_scale.set(0)
    q1_label.configure(text="0")
    q2_scale.set(0)
    q2_label.configure(text="0")
    q3_scale.set(0)
    q3_label.configure(text="0")
    grade_scale.set(0)
    grade_label.configure(text="0")
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
                f"{record['student_id'].strip()},{int(record['q1'])},{int(record['q2'])},{int(record['q3'])},{int(record['grade'])},{' | '.join(record['feedback'])},{'Yes' if record['attention'] else 'No'},{record['file_path']}\n"
            )


def get_feedback():
    feedback = []
    if feedback_var1.get():
        feedback.append("Strong overall performance")
    if feedback_var2.get():
        feedback.append("Specific areas need improvement")
    if feedback_var3.get():
        feedback.append("Unexplained grade variations")
    if feedback_var4.get():
        feedback.append("Limited participation observed")
    if feedback_var_other.get():
        feedback.append(
            f"{'Other: ' + other_entry.get().strip() if other_entry.get().strip() else 'Other'}"
        )
    return feedback


def set_feedback(feedback):
    feedback_var1.set("Strong overall performance" in feedback)
    feedback_var2.set("Specific areas need improvement" in feedback)
    feedback_var3.set("Unexplained grade variations" in feedback)
    feedback_var4.set("Limited participation observed" in feedback)
    if feedback:
        feedback_var_other.set("Other" in feedback[-1])
    if feedback_var_other.get():
        other_entry.configure(state="normal")
    else:
        other_entry.configure(state="disabled")
    if feedback and "Other: " in feedback[-1]:
        other_entry.insert(0, feedback[-1].strip("Other: "))


def clear_feedback():
    feedback_var1.set(False)
    feedback_var2.set(False)
    feedback_var3.set(False)
    feedback_var4.set(False)
    feedback_var_other.set(False)
    other_entry.delete(0, tk.END)
    other_entry.configure(state="disabled")


root = tk.CTk()
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()
# x = math.floor(1.6 * screen_width)
# y = math.floor(0.1 * screen_height)
# root.geometry(f"870x720+{x}+{y}")

root.title("Tiny Studium")
root.resizable(False, False)
root.iconbitmap("themes/ico/stu.svg")
tk.set_appearance_mode("dark")
tk.set_default_color_theme("themes/Cobalt.json")

tk.CTkLabel(root, text="Student ID: ").grid(row=0, column=0, sticky="e")
student_id_entry = tk.CTkEntry(root, width=230)
student_id_entry.grid(row=0, column=1, columnspan=7, padx=10, pady=10, sticky="w")
student_id_entry.bind("<Key>", lambda event: log_event(event, "Student ID"))
student_id_entry.bind("<FocusIn>", lambda event: log_event(event, "Student ID"))


def show_slider_val(value, label):
    label.configure(text=int(value))


tk.CTkLabel(root, text="Q1: ").grid(row=1, column=0, sticky="e")
q1_label = tk.CTkLabel(root, text="0")
q1_label.grid(row=1, column=1, sticky="e")
q1_scale = tk.CTkSlider(
    root,
    from_=0,
    to=100,
    number_of_steps=100,
    command=lambda value: show_slider_val(value, q1_label),
)
q1_scale.set(0)
q1_scale.grid(row=1, column=1, padx=10, pady=10)
q1_scale.bind(
    "<ButtonRelease>", lambda event: log_event(event, "Q1", q1_label.cget("text"))
)
q1_scale.bind("<Key>", lambda event: log_event(event, "Q1"))
q1_scale.bind("<FocusIn>", lambda event: log_event(event, "Q1"))

tk.CTkLabel(root, text="Q2: ").grid(row=2, column=0, sticky="e")
q2_label = tk.CTkLabel(root, text="0")
q2_label.grid(row=2, column=1, sticky="e")
q2_scale = tk.CTkSlider(
    root,
    from_=0,
    to=100,
    number_of_steps=100,
    command=lambda value: show_slider_val(value, q2_label),
)
q2_scale.set(0)
q2_scale.grid(row=2, column=1, padx=10, pady=10)
q2_scale.bind(
    "<ButtonRelease>", lambda event: log_event(event, "Q2", q2_label.cget("text"))
)
q2_scale.bind("<Key>", lambda event: log_event(event, "Q2"))
q2_scale.bind("<FocusIn>", lambda event: log_event(event, "Q2"))

tk.CTkLabel(root, text="Q3: ").grid(row=3, column=0, sticky="e")
q3_label = tk.CTkLabel(root, text="0")
q3_label.grid(row=3, column=1, sticky="e")
q3_scale = tk.CTkSlider(
    root,
    from_=0,
    to=100,
    number_of_steps=100,
    command=lambda value: show_slider_val(value, q3_label),
)
q3_scale.set(0)
q3_scale.grid(row=3, column=1, padx=10, pady=10)
q3_scale.bind(
    "<ButtonRelease>", lambda event: log_event(event, "Q3", q3_label.cget("text"))
)
q3_scale.bind("<Key>", lambda event: log_event(event, "Q3"))
q3_scale.bind("<FocusIn>", lambda event: log_event(event, "Q3"))

tk.CTkLabel(root, text="Total grade: ").grid(row=4, column=0, sticky="e")
grade_label = tk.CTkLabel(root, text="0")
grade_label.grid(row=4, column=1, sticky="e")
grade_scale = tk.CTkSlider(
    root,
    from_=0,
    to=100,
    number_of_steps=100,
    command=lambda value: show_slider_val(value, grade_label),
)
grade_scale.set(0)
grade_scale.grid(row=4, column=1, padx=10, pady=10)
grade_scale.bind(
    "<ButtonRelease>",
    lambda event: log_event(event, "Total grade", grade_label.cget("text")),
)
grade_scale.bind("<Key>", lambda event: log_event(event, "Total grade"))
grade_scale.bind("<FocusIn>", lambda event: log_event(event, "Total grade"))

separator = ttk.Separator(root, orient="horizontal")
separator.grid(row=5, column=0, columnspan=8, sticky="nsew", pady=30, padx=100)

feedback_var1 = tk.BooleanVar()
feedback_var2 = tk.BooleanVar()
feedback_var3 = tk.BooleanVar()
feedback_var4 = tk.BooleanVar()
feedback_var_other = tk.BooleanVar()


tk.CTkLabel(root, text="Student feedback: ").grid(row=6, column=0, sticky="ne")
sf1_check = tk.CTkCheckBox(
    root, text="Strong overall performance", variable=feedback_var1
)
sf1_check.grid(row=6, column=1, sticky="w", pady=5, padx=10)
sf1_check.bind(
    "<space>",
    lambda event: log_chk_state(event, feedback_var1, "Strong overall performance"),
)
sf1_check.bind(
    "<Button-1>",
    lambda event: log_chk_state(event, feedback_var1, "Strong overall performance"),
)

sf2_check = tk.CTkCheckBox(
    root, text="Specific areas need improvement", variable=feedback_var2
)
sf2_check.grid(row=7, column=1, sticky="w", pady=5, padx=10)
sf2_check.bind(
    "<space>",
    lambda event: log_chk_state(
        event, feedback_var2, "Specific areas need improvement"
    ),
)
sf2_check.bind(
    "<Button-1>",
    lambda event: log_chk_state(
        event, feedback_var2, "Specific areas need improvement"
    ),
)

sf3_check = tk.CTkCheckBox(
    root, text="Unexplained grade variations", variable=feedback_var3
)
sf3_check.grid(row=8, column=1, sticky="w", pady=5, padx=10)
sf3_check.bind(
    "<space>",
    lambda event: log_chk_state(event, feedback_var3, "Unexplained grade variations"),
)
sf3_check.bind(
    "<Button-1>",
    lambda event: log_chk_state(event, feedback_var3, "Unexplained grade variations"),
)

sf4_check = tk.CTkCheckBox(
    root, text="Limited participation observed", variable=feedback_var4
)
sf4_check.grid(row=9, column=1, sticky="w", pady=5, padx=10)
sf4_check.bind(
    "<space>",
    lambda event: log_chk_state(event, feedback_var4, "Limited participation observed"),
)
sf4_check.bind(
    "<Button-1>",
    lambda event: log_chk_state(event, feedback_var4, "Limited participation observed"),
)

other_check = tk.CTkCheckBox(
    root,
    text="Other",
    variable=feedback_var_other,
    command=lambda: toggle_textbox(feedback_var_other, other_entry),
)
other_check.grid(row=10, column=1, sticky="w", pady=5, padx=10)
other_check.bind(
    "<space>", lambda event: log_chk_state(event, feedback_var_other, "Other")
)
other_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, feedback_var_other, "Other")
)
other_entry = tk.CTkEntry(root, width=200, state="disabled")
other_entry.grid(row=10, column=1, padx=10, pady=5, sticky="e")
other_entry.bind("<Key>", lambda event: log_event(event, "Other text"))
other_entry.bind("<FocusIn>", lambda event: log_event(event, "Other text"))


def toggle_textbox(var, textbox):
    if var.get():
        textbox.configure(state="normal")
    else:
        textbox.delete(0, tk.END)
        textbox.configure(state="disabled")


tk.CTkLabel(root, text="Mark for attention: ").grid(row=11, column=0, sticky="e")
flag_var = tk.BooleanVar()
flag_check = tk.CTkCheckBox(root, variable=flag_var, text="")
flag_check.grid(row=11, column=1, sticky="w", pady=5, padx=10)
flag_check.bind(
    "<space>", lambda event: log_chk_state(event, flag_var, "Mark for attention")
)
flag_check.bind(
    "<Button-1>", lambda event: log_chk_state(event, flag_var, "Mark for attention")
)

tk.CTkLabel(root, text="Additional doc (optional): ").grid(row=12, column=0, sticky="e")
file_path_label = tk.CTkLabel(
    root, text="Comments, docs, images related to the student"
)
file_path_label.grid(row=12, column=1, columnspan=7, sticky="e", padx=60, pady=10)

grades_widget_names = ["Q1", "Q2", "Q3", "Total grade"]
widget_names = {
    student_id_entry: "Student ID",
    q1_scale: "Q1",
    q2_scale: "Q2",
    q3_scale: "Q3",
    grade_scale: "Total grade",
    sf1_check: "Strong overall performance",
    sf2_check: "Specific areas need improvement",
    sf3_check: "Unexplained grade variations",
    sf4_check: "Limited participation observed",
    other_check: "Other",
    other_entry: "Other text",
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
upload_button.grid(row=12, column=1, columnspan=7, sticky="w", padx=10, pady=10)

save_button = tk.CTkButton(
    root,
    text="Save current record",
    command=save_data,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/save.png"), size=(24, 24)),
    compound=tk.LEFT,
)
save_button.grid(row=13, column=1, columnspan=7, sticky="e", padx=100, pady=(40, 10))

separator1 = ttk.Separator(root, orient="horizontal")
separator1.grid(row=14, column=0, columnspan=8, sticky="nsew", pady=30)

view_button = tk.CTkButton(
    root,
    text="View already entered records",
    command=view_records,
    image=tk.CTkImage(Image.open("themes/ico/view.png"), size=(24, 24)),
    compound=tk.LEFT,
)
view_button.grid(row=15, column=0, sticky="w", padx=10, pady=10)

feedback_button = tk.CTkButton(
    root,
    text="Provide overall feedback to instructor",
    command=add_overall_feedback,
    image=tk.CTkImage(Image.open("themes/ico/feedback.png"), size=(24, 24)),
    compound=tk.LEFT,
)
feedback_button.grid(row=15, column=1, columnspan=6, sticky="w", padx=10, pady=10)

submit_button = tk.CTkButton(
    root,
    text="Submit all records",
    command=proceed_to_submit_records,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/all.png"), size=(24, 24)),
    compound=tk.LEFT,
)
submit_button.grid(row=15, column=7, sticky="e", padx=10, pady=10)

log(f"Form - Started")
root.mainloop()
log(f"Form - Destroyed")
