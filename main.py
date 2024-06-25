import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import cv2
import threading

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Приложение для обработки изображений")
        self.image = None
        self.original_image = None
        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.create_widgets()

    def create_widgets(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        upload_btn = tk.Button(btn_frame, text="Загрузить изображение", command=self.upload_image)
        upload_btn.grid(row=0, column=0, padx=5, pady=5)

        webcam_btn = tk.Button(btn_frame, text="Использовать веб-камеру", command=self.start_webcam_thread)
        webcam_btn.grid(row=0, column=1, padx=5, pady=5)

        channel_label = tk.Label(btn_frame, text="Список каналов")
        channel_label.grid(row=1, column=0, padx=5, pady=5)
        
        self.channel_var = tk.StringVar(value="Красный")
        channel_menu = tk.OptionMenu(btn_frame, self.channel_var, "Красный", "Зеленый", "Синий", command=self.show_channel)
        channel_menu.grid(row=2, column=0, padx=5, pady=5)

        crop_btn = tk.Button(btn_frame, text="Обрезать изображение", command=self.crop_image)
        crop_btn.grid(row=2, column=1, padx=5, pady=5)

        avg_btn = tk.Button(btn_frame, text="Применить фильтр усреднения", command=self.apply_average_filter)
        avg_btn.grid(row=3, column=0, padx=5, pady=5)

        draw_circle_btn = tk.Button(btn_frame, text="Нарисовать круг", command=self.draw_circle)
        draw_circle_btn.grid(row=3, column=1, padx=5, pady=5)

        reset_btn = tk.Button(btn_frame, text="Сбросить изменения", command=self.reset_image)
        reset_btn.grid(row=4, column=0, padx=5, pady=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg")])
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.original_image = self.image.copy()
                self.display_image(self.image)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")

    def start_webcam_thread(self):
        webcam_thread = threading.Thread(target=self.use_webcam)
        webcam_thread.daemon = True
        webcam_thread.start()
        
    def use_webcam(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Ошибка", "Не удалось открыть веб-камеру")
                return

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow('Press 2 to exit, 1 to save image', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('2'):
                    break
                elif key == ord('1'):
                    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.image = Image.fromarray(image_rgb)
                    self.original_image = self.image.copy()  
                    self.display_image(self.image)

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        finally:
            if cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()

    def display_image(self, image):
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.tk_image)

    def show_channel(self, _):
        if not self.original_image:
            messagebox.showerror("Ошибка", "Изображение не загружено")
            return

        channel_name = self.channel_var.get()
        if channel_name not in ["Красный", "Зеленый", "Синий"]:
            messagebox.showerror("Ошибка", "Неверно выбран канал")
            return

        if self.original_image.mode == 'RGBA':
            r, g, b, a = self.original_image.split()
        else:
            r, g, b = self.original_image.split()
            a = Image.new("L", r.size, 255) 

        if channel_name == "Красный":
            img = Image.merge("RGBA", (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0), a))
        elif channel_name == "Зеленый":
            img = Image.merge("RGBA", (Image.new("L", g.size, 0), g, Image.new("L", g.size, 0), a))
        else:
            img = Image.merge("RGBA", (Image.new("L", b.size, 0), Image.new("L", b.size, 0), b, a))

        self.image = img
        self.display_image(img)

    def crop_image(self):
        if not self.image:
            messagebox.showerror("Ошибка", "Изображение не загружено")
            return
        user_input = self.simple_input("Введите координаты обрезки (x1, y1, x2, y2):")
        if not user_input:
            return
        try:
            x1, y1, x2, y2 = map(int, user_input.split())
            cropped = self.image.crop((x1, y1, x2, y2))
            self.image = cropped
            self.display_image(cropped)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

    def apply_average_filter(self):
        if not self.image:
            messagebox.showerror("Ошибка", "Изображение не загружено")
            return

        try:
            kernel_size = int(simpledialog.askstring("Фильтр усреднения", "Введите размер ядра (например, 3 для 3x3):"))
            if kernel_size <= 0 or kernel_size % 2 == 0:
                messagebox.showerror("Ошибка", "Размер ядра должен быть положительным нечетным числом")
                return

            filtered_image = self.image.filter(ImageFilter.BoxBlur(kernel_size))
            self.image = filtered_image
            self.display_image(filtered_image)

        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ввод: введите целое число")

    def draw_circle(self):
        if not self.image:
            messagebox.showerror("Ошибка", "Изображение не загружено")
            return
        user_input = self.simple_input("Введите координаты и радиус круга (x, y, r):")
        if not user_input:
            return
        try:
            x, y, r = map(int, user_input.split())
            img_copy = self.image.copy()
            draw = ImageDraw.Draw(img_copy)
            draw.ellipse((x-r, y-r, x+r, y+r), outline="red", width=3)
            self.image = img_copy
            self.display_image(img_copy)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.display_image(self.image)
        else:
            messagebox.showerror("Ошибка", "Исходное изображение отсутствует")

    def simple_input(self, prompt):
        user_input = simpledialog.askstring("Ввод", prompt)
        if user_input is None or user_input.strip() == "":
            return None
        return user_input

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
