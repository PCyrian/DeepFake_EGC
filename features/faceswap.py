import cv2
import dlib
import numpy as np
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Load the required models
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


def extract_landmarks(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector(gray)
    if len(faces) == 0:
        return None, None
    landmarks = []
    for face in faces:
        shape = landmark_predictor(gray, face)
        landmarks.append([(p.x, p.y) for p in shape.parts()])
    return faces, landmarks


def warp_triangle(src, dst, t1, t2):
    warp_mat = cv2.getAffineTransform(np.float32(t1), np.float32(t2))
    warped_triangle = cv2.warpAffine(src, warp_mat, (dst.shape[1], dst.shape[0]), None, flags=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_REFLECT_101)

    mask = np.zeros(dst.shape, dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(t2), (255, 255, 255))
    dst[mask == 255] = warped_triangle[mask == 255]


def face_swap(image1_path, image2_path, output_path):
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    faces1, landmarks1 = extract_landmarks(image1)
    faces2, landmarks2 = extract_landmarks(image2)

    if landmarks1 is None or landmarks2 is None:
        messagebox.showerror("Error", "Could not detect faces in one or both images.")
        return

    hull1 = cv2.convexHull(np.array(landmarks1[0]), returnPoints=False)
    hull2 = cv2.convexHull(np.array(landmarks2[0]), returnPoints=False)

    # Create a subdivided bounding rectangle for triangles
    rect = cv2.boundingRect(np.array(landmarks2[0]))
    subdiv = cv2.Subdiv2D(rect)
    for p in landmarks2[0]:
        subdiv.insert(p)

    triangles = subdiv.getTriangleList()

    img1_warped = np.copy(image2)

    for triangle in triangles:
        # Ensure each triangle has exactly 3 points
        t1 = [landmarks1[0][i] for i in cv2.convexHull(np.array(landmarks1[0]), returnPoints=False).flatten()]
        t2 = [landmarks2[0][i] for i in cv2.convexHull(np.array(landmarks2[0]), returnPoints=False).flatten()]

        # Only process if there are exactly 3 points in both t1 and t2
        if len(t1) == 3 and len(t2) == 3:
            warp_triangle(image1, img1_warped, t1, t2)

    # Prepare mask for seamless cloning
    mask = np.zeros(image2.shape, dtype=np.uint8)
    hull2 = np.array(landmarks2[0], dtype=np.int32)
    cv2.fillConvexPoly(mask, hull2, (255, 255, 255))

    r = cv2.boundingRect(hull2)
    center = (r[0] + r[2] // 2, r[1] + r[3] // 2)

    output = cv2.seamlessClone(np.uint8(img1_warped), image2, mask, center, cv2.NORMAL_CLONE)

    cv2.imwrite(output_path, output)
    messagebox.showinfo("Success", f"Face swapped image saved at {output_path}")


# GUI setup with customtkinter
class FaceSwapApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Face Swap Application")
        self.geometry("400x300")

        self.image1_path = None
        self.image2_path = None

        self.label1 = ctk.CTkLabel(self, text="Select first image")
        self.label1.pack(pady=10)
        self.button1 = ctk.CTkButton(self, text="Browse", command=self.browse_image1)
        self.button1.pack(pady=10)

        self.label2 = ctk.CTkLabel(self, text="Select second image")
        self.label2.pack(pady=10)
        self.button2 = ctk.CTkButton(self, text="Browse", command=self.browse_image2)
        self.button2.pack(pady=10)

        self.process_button = ctk.CTkButton(self, text="Process", command=self.process_images)
        self.process_button.pack(pady=20)

    def browse_image1(self):
        self.image1_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.image1_path:
            self.label1.configure(text=self.image1_path)

    def browse_image2(self):
        self.image2_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.image2_path:
            self.label2.configure(text=self.image2_path)

    def process_images(self):
        if not self.image1_path or not self.image2_path:
            messagebox.showerror("Error", "Please select both images.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        if output_path:
            face_swap(self.image1_path, self.image2_path, output_path)


if __name__ == "__main__":
    app = FaceSwapApp()
    app.mainloop()
