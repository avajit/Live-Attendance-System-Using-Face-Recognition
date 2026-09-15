import os
import numpy as np
from PIL import Image
import json
from sklearn.neighbors import KNeighborsClassifier
from keras_facenet import FaceNet

def train_model():
    embedder = FaceNet()  # Load pretrained FaceNet model

    faces, ids = [], []
    label_map = {}
    current_id = 0

    if not os.path.exists('student_images'):
        print("❌ 'student_images' folder not found. Please register students first.")
        return

    student_folders = os.listdir('student_images')

    for folder in student_folders:
        folder_path = os.path.join('student_images', folder)
        if not os.path.isdir(folder_path):
            continue

        label = folder  # Example: '001_John'
        if label not in label_map:
            label_map[label] = current_id
            current_id += 1

        id_ = label_map[label]

        for img_file in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_file)

            if not os.path.isfile(img_path):
                continue

            # Skip non-image files
            if not img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                continue

            try:
                img = Image.open(img_path).convert('RGB')
                img_np = np.array(img)
            except Exception as e:
                print(f"❌ Skipping '{img_path}': {e}")
                continue

            # Extract FaceNet embedding
            embeddings = embedder.embeddings([img_np])  
            if embeddings is not None:
                faces.append(embeddings[0])
                ids.append(id_)

    if len(faces) == 0:
        print("❌ No faces found to train. Please check your images.")
        return

    # Train a classifier on embeddings (here we use KNN)
    knn = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
    knn.fit(faces, ids)

    # Save embeddings and labels
    np.save("faces_embeddings.npy", faces)
    np.save("faces_labels.npy", ids)

    with open("label_map.json", "w") as f:
        json.dump(label_map, f)

    print("✅ Training complete. Embeddings saved as 'faces_embeddings.npy', labels as 'faces_labels.npy', and label map as 'label_map.json'")

if __name__ == "__main__":
    train_model()
