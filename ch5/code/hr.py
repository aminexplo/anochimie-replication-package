import os
import shutil
from datetime import datetime
import customtkinter as tk
from tkinter import messagebox, filedialog, ttk, Listbox, Scrollbar
from tkinter.colorchooser import askcolor
from tkcalendar import DateEntry
from PIL import Image
import math

main_dir = "m_employee_onboarding/logs"
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

os.makedirs(f"{main_dir}/{user_name}",exist_ok=True)


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
    employee_id = id_entry.get()
    log(f"Save clicked - ID: {'No ID' if not employee_id else employee_id.strip()}")

    if not employee_id:
        log("Please enter an ID before saving a record.")
        messagebox.showwarning("Warning", "Please enter an ID before saving a record.")
        return

    global selected_record_index

    record = {
        "id": employee_id,
        "phone_number": tel_entry.get(),
        "start_date": start_date_entry.get(),
        "position": position_var.get(),
        "amenities": get_amenities(),
        "working_hours": working_hours_slider.get(),
        "uniform_color": color_var.get(),
        "file_path": uploaded_files.get(employee_id, ""),
    }

    if selected_record_index is not None:
        records[selected_record_index] = record
        selected_record_index = None
    else:
        records.append(record)

    clear_entries()
    save_records_to_file()


def get_amenities():
    amenities = []
    if amenity_var1.get():
        amenities.append("Laptop")
    if amenity_var2.get():
        amenities.append("Furniture")
    if amenity_var3.get():
        amenities.append("Private office")
    if amenity_var4.get():
        amenities.append("Fan")
    if amenity_var5.get():
        amenities.append("Floor lamp")

    return amenities


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
        tel_entry.delete(0, tk.END)
        tel_entry.insert(0, record["phone_number"])
        start_date_entry.set_date(record["start_date"])
        position_var.set(record["position"])

        amenities = record["amenities"]
        amenity_var1.set("Laptop" in amenities)
        amenity_var2.set("Furniture" in amenities)
        amenity_var3.set("Private office" in amenities)
        amenity_var4.set("Fan" in amenities)
        amenity_var5.set("Floor lamp" in amenities)

        wh = int(record["working_hours"])
        working_hours_slider.set(wh)
        working_hours_label.configure(text=wh)
        color_var.set(record["uniform_color"])
        color_label.configure(bg_color=record["uniform_color"])

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
            f"ID: {record['id']} - Phone number: {record['phone_number']} - Start Date: {record['start_date']} - Position: {record['position']} - Amenities: {' | '.join(record['amenities'])} - Working Hours: {int(record['working_hours'])} - Uniform Color: {record['uniform_color']} - File: {os.path.basename(record['file_path'])}",
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
        text="Overall comments for the HR manager (optional): ",
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
    tel_entry.delete(0, tk.END)
    start_date_entry.set_date(datetime.now())
    position_var.set("")

    amenity_var1.set(False)
    amenity_var2.set(False)
    amenity_var3.set(False)
    amenity_var4.set(False)
    amenity_var5.set(False)

    working_hours_slider.set(0)
    working_hours_label.configure(text="0")
    color_var.set("blue")
    color_label.configure(bg_color="blue")
    file_path_label.configure(text="Comments, docs, images related to the employee")


def upload_file():
    log("Upload file clicked")
    root.focus_set()
    file_path = filedialog.askopenfilename()
    if file_path:
        employee_id = id_entry.get()
        if not employee_id:
            log("Please enter an ID before uploading a file.")
            messagebox.showwarning(
                "Warning", "Please enter a ID before uploading a file."
            )
            return
        new_file_name = f"{main_dir}/{user_name}/{employee_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(file_path)}"
        shutil.copy(file_path, new_file_name)
        uploaded_files[employee_id] = new_file_name
        log(f"File uploaded for {employee_id}: {new_file_name}")
        messagebox.showinfo("File Upload", f"File uploaded: {new_file_name}")
        file_path_label.configure(text=f"File: {os.path.basename(new_file_name)}")
        root.focus_set()


def save_records_to_file():
    with open(data_file_name, "w") as data_file:
        write_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_file.write(f"---\n{write_time}\n---\n")
        for record in records:
            data_file.write(
                f"{record['id'].strip()},{record['phone_number'].strip()},{record['start_date'].strip()},{record['position'].strip()},{' | '.join(record['amenities']).strip()},{int(record['working_hours'])},{record['uniform_color'].strip()},{record['file_path']}\n"
            )


root = tk.CTk()
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()
# x = math.floor(1.6 * screen_width)
# y = math.floor(0.1 * screen_height)
# root.geometry(f"870x585+{x}+{y}")

root.title("Employee Onboarding")
root.resizable(False, False)
root.iconbitmap("themes/ico/stu.svg")
tk.set_appearance_mode("dark")
tk.set_default_color_theme("themes/Cobalt.json")

# GUI elements
tk.CTkLabel(root, text="ID: ").grid(row=0, column=0, padx=10, pady=10, sticky="e")
id_entry = tk.CTkEntry(root)
id_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
id_entry.bind("<Key>", lambda event: log_event(event, "ID"))
id_entry.bind("<FocusIn>", lambda event: log_event(event, "ID"))


def limit_char(*args):
    value = char_string_var.get()
    if len(value) > max_chars:
        char_string_var.set(value[:max_chars])


max_chars = 38
char_string_var = tk.StringVar()
char_string_var.trace_add("write", limit_char)

tk.CTkLabel(root, text="Phone number: ").grid(
    row=0, column=2, padx=10, pady=10, sticky="e"
)
tel_entry = tk.CTkEntry(root, textvariable=char_string_var)
tel_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")
tel_entry.bind("<Key>", lambda event: log_event(event, "Phone number"))
tel_entry.bind("<FocusIn>", lambda event: log_event(event, "Phone number"))

tk.CTkLabel(root, text="Job start date: ").grid(
    row=1, column=0, padx=10, pady=10, sticky="e"
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
start_date_entry = DateEntry(
    root, style="my.DateEntry", font=("Roboto Condensed", 18), locale="en_CA"
)
start_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
start_date_entry.bind(
    "<<DateEntrySelected>>", lambda event: log_event(event, "Job start date")
)
start_date_entry.bind("<FocusIn>", lambda event: log_event(event, "Job start date"))

tk.CTkLabel(root, text="Position title: ").grid(
    row=1, column=2, padx=10, pady=10, sticky="e"
)


def combobox_callback(choice):
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"Position title - ComboboxSelected - {choice}", event_time)


position_var = tk.StringVar()
position_entry = tk.CTkComboBox(
    master=root,
    values=[
        "Software Engineer",
        "Product Manager",
        "Data Scientist",
        "Designer",
        "Sales Manager",
    ],
    command=combobox_callback,
    variable=position_var,
)
position_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
position_entry.bind("<Key>", lambda event: log_event(event, "Position title"))
position_entry.bind("<FocusIn>", lambda event: log_event(event, "Position title"))

tk.CTkLabel(root, text="Workplace amenities: ").grid(
    row=2, column=0, padx=10, pady=10, sticky="e"
)
amenity_var1 = tk.BooleanVar()
amenity_var2 = tk.BooleanVar()
amenity_var3 = tk.BooleanVar()
amenity_var4 = tk.BooleanVar()
amenity_var5 = tk.BooleanVar()

amenity_chk1 = tk.CTkCheckBox(root, text="Laptop", variable=amenity_var1)
amenity_chk1.grid(row=2, column=1, padx=10, pady=10, sticky="w")
amenity_chk1.bind("<space>", lambda event: log_chk_state(event, amenity_var1, "Laptop"))
amenity_chk1.bind(
    "<Button-1>", lambda event: log_chk_state(event, amenity_var1, "Laptop")
)

amenity_chk2 = tk.CTkCheckBox(root, text="Furniture", variable=amenity_var2)
amenity_chk2.grid(row=3, column=1, padx=10, pady=10, sticky="w")
amenity_chk2.bind(
    "<space>", lambda event: log_chk_state(event, amenity_var2, "Furniture")
)
amenity_chk2.bind(
    "<Button-1>", lambda event: log_chk_state(event, amenity_var2, "Furniture")
)

amenity_chk3 = tk.CTkCheckBox(root, text="Private office", variable=amenity_var3)
amenity_chk3.grid(row=4, column=1, padx=10, pady=10, sticky="w")
amenity_chk3.bind(
    "<space>", lambda event: log_chk_state(event, amenity_var3, "Private office")
)
amenity_chk3.bind(
    "<Button-1>", lambda event: log_chk_state(event, amenity_var3, "Private office")
)

amenity_chk4 = tk.CTkCheckBox(root, text="Fan", variable=amenity_var4)
amenity_chk4.grid(row=5, column=1, padx=10, pady=10, sticky="w")
amenity_chk4.bind("<space>", lambda event: log_chk_state(event, amenity_var4, "Fan"))
amenity_chk4.bind("<Button-1>", lambda event: log_chk_state(event, amenity_var4, "Fan"))

amenity_chk5 = tk.CTkCheckBox(root, text="Floor lamp", variable=amenity_var5)
amenity_chk5.grid(row=6, column=1, padx=10, pady=10, sticky="w")
amenity_chk5.bind(
    "<space>", lambda event: log_chk_state(event, amenity_var5, "Floor lamp")
)
amenity_chk5.bind(
    "<Button-1>", lambda event: log_chk_state(event, amenity_var5, "Floor lamp")
)


def show_slider_val(value, label):
    label.configure(text=int(value))


tk.CTkLabel(root, text="Remote work hours per week: ").grid(
    row=2, column=2, padx=10, pady=10, sticky="e"
)
working_hours_slider = tk.CTkSlider(
    root,
    from_=0,
    to=40,
    number_of_steps=40,
    width=160,
    command=lambda value: show_slider_val(value, working_hours_label),
)
working_hours_slider.set(0)
working_hours_slider.grid(row=2, column=3, padx=10, pady=10, sticky="e")
working_hours_label = tk.CTkLabel(root, text="0")
working_hours_label.grid(row=2, column=3, padx=10, pady=10, sticky="w")
working_hours_slider.bind(
    "<ButtonRelease>",
    lambda event: log_event(
        event, "Remote work hours per week", working_hours_label.cget("text")
    ),
)
working_hours_slider.bind(
    "<Key>", lambda event: log_event(event, "Remote work hours per week")
)
working_hours_slider.bind(
    "<FocusIn>", lambda event: log_event(event, "Remote work hours per week")
)


def pick_color():
    log("Choose color clicked")
    root.focus_set()
    color = askcolor()[1]
    if color:
        color_var.set(color)
        color_label.configure(bg_color=color)
        event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log(f"Choose color - ColorSelected - {color}", event_time)

    root.focus_set()


tk.CTkLabel(root, text="Uniform color: ").grid(
    row=3, column=2, padx=10, pady=10, sticky="e"
)
color_var = tk.StringVar()
color_var.set("blue")
color_label = tk.CTkLabel(root, text=" ", bg_color="blue", width=30)
color_label.grid(row=3, column=3, padx=10, pady=10, sticky="w")
pick_color_button = tk.CTkButton(
    root,
    text="Choose color",
    command=pick_color,
    image=tk.CTkImage(Image.open("themes/ico/color.png"), size=(24, 24)),
    compound=tk.LEFT,
)
pick_color_button.grid(row=3, column=3, padx=10, pady=10, sticky="e")

tk.CTkLabel(root, text="Additional doc (optional): ").grid(
    row=8, column=0, padx=10, pady=10, sticky="e"
)
tk.CTkButton(
    root,
    text="Upload file",
    command=upload_file,
    image=tk.CTkImage(Image.open("themes/ico/upload.png"), size=(24, 24)),
    compound=tk.LEFT,
).grid(row=8, column=1, padx=10, pady=10, sticky="w")
file_path_label = tk.CTkLabel(
    root, text="Comments, docs, images related to the employee"
)
file_path_label.grid(row=8, column=2, columnspan=2, sticky="w", padx=60, pady=10)

# Buttons
save_button = tk.CTkButton(
    root,
    text="Save current record",
    command=save_data,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/save.png"), size=(24, 24)),
    compound=tk.LEFT,
)
save_button.grid(row=9, column=3, sticky="w", padx=10, pady=(40, 10))

separator1 = ttk.Separator(root, orient="horizontal")
separator1.grid(row=10, column=0, columnspan=4, sticky="nsew", pady=30)

view_button = tk.CTkButton(
    root,
    text="View already entered records",
    command=view_records,
    image=tk.CTkImage(Image.open("themes/ico/view.png"), size=(24, 24)),
    compound=tk.LEFT,
)
view_button.grid(row=11, column=0, columnspan=2, sticky="w", padx=10, pady=10)

feedback_button = tk.CTkButton(
    root,
    text="Provide overall comment to HR",
    command=add_overall_feedback,
    image=tk.CTkImage(Image.open("themes/ico/feedback.png"), size=(24, 24)),
    compound=tk.LEFT,
)
feedback_button.grid(row=11, column=1, columnspan=3, sticky="w", padx=(90, 0), pady=10)

submit_button = tk.CTkButton(
    root,
    text="Submit all records",
    command=proceed_to_submit_records,
    fg_color="darkblue",
    image=tk.CTkImage(Image.open("themes/ico/all.png"), size=(24, 24)),
    compound=tk.LEFT,
)
submit_button.grid(row=11, column=3, sticky="e", padx=(20, 5), pady=10)


log(f"Form - Started")
root.mainloop()
log(f"Form - Destroyed")
