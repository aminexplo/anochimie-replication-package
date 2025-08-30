import customtkinter
from typing import Union, Callable


class WidgetName(customtkinter.CTkFrame):
    def __init__(self, *args, width: int = 100, height: int = 32, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)


class CTkSpinbox(customtkinter.CTkFrame):
    def __init__(
        self,
        *args,
        width: int = 100,
        height: int = 32,
        step_size: int = 1,
        min: int = -100,
        max: int = 100,
        command: Callable = None,
        **kwargs
    ):
        super().__init__(*args, width=width, height=height, **kwargs)

        vspincmd = None
        for arg in args:
            if isinstance(arg, customtkinter.CTk):
                vspincmd = arg.register(self.validate_spin_input)
            else:
                continue

        self.step_size = step_size
        self.min = min
        self.max = max
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(
            self,
            text="-",
            width=height - 6,
            height=height - 6,
            command=self.subtract_button_callback,
        )
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(
            self,
            width=width - (2 * height),
            height=height - 6,
            border_width=0,
            validate="all",
            validatecommand=(vspincmd, "%P"),
        )
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        self.entry.bind("<Key>", self.on_key_press)
        self.entry.bind("<FocusIn>", self.on_focus_in)

        self.add_button = customtkinter.CTkButton(
            self,
            text="+",
            width=height - 6,
            height=height - 6,
            command=self.add_button_callback,
        )
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)
        self.add_button.bind("<ButtonRelease>", self.on_button_release)

        self.entry.insert(0, "0")

    def validate_spin_input(self, new_value):
        temp = str(new_value).strip()
        new_value_pruned = temp.replace("-", "").replace(".", "")
        if self._is_num_and_in_range(temp):
            new_value = int(temp)

        if (
            self._is_num_and_in_range(new_value)
            or new_value == ""
            or new_value == "-"
        ) and len(new_value_pruned) <= 4:
            return True
        else:
            return False

    def _is_num_and_in_range(self, n):
        try:
            num = int(n)
            return num >= self.min and num <= self.max
        except ValueError:
            return False

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[int, None]:
        try:
            return int(self.entry.get())
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(round(int(value), 2)))


    def on_button_release(self, event):
        pass

    def on_key_press(self, event):
        pass

    def on_focus_in(self, event):
        pass