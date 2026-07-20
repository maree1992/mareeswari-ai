import os
import zipfile
from io import BytesIO

import imagehash
import numpy as np
import streamlit as st
from PIL import Image

try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    face_recognition = None
    HAS_FACE_RECOGNITION = False

VALID_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

st.set_page_config(page_title="Image Folder Viewer", layout="wide")
st.title("Image Folder Viewer")

st.markdown(
    "Use a local folder or upload a set of images/ZIP. "
    "Then upload one reference image to find matching faces or visually similar images."
)

source = st.radio("Image source", ["Local folder", "Uploaded images/ZIP"], index=0)

folder_path = ""
uploaded_inputs = []
if source == "Local folder":
    folder_path = st.text_input("Folder path", value="")
    if folder_path and not os.path.isdir(folder_path):
        st.error("Folder not found. Please enter a valid local folder path.")
else:
    uploaded_inputs = st.file_uploader(
        "Upload images or a ZIP archive",
        type=["png", "jpg", "jpeg", "gif", "bmp", "webp", "zip"],
        accept_multiple_files=True,
    )


def is_valid_image(name: str) -> bool:
    return name.lower().endswith(VALID_IMAGE_EXTS)


def load_image_from_bytes(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data)).convert("RGB")


def prepare_uploaded_candidates(files):
    candidates = []
    for uploaded_file in files:
        name = uploaded_file.name
        data = uploaded_file.getbuffer()
        if name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(BytesIO(data)) as z:
                    for member in z.namelist():
                        if member.endswith("/"):
                            continue
                        if is_valid_image(member):
                            candidate_bytes = z.read(member)
                            candidates.append({
                                "name": os.path.basename(member),
                                "path": None,
                                "bytes": candidate_bytes,
                            })
            except Exception as err:
                st.warning(f"Could not read ZIP file {name}: {err}")
        elif is_valid_image(name):
            candidates.append({"name": name, "path": None, "bytes": data})
    return candidates


def prepare_local_candidates(path):
    candidates = []
    if not path:
        return candidates
    for fn in sorted(os.listdir(path)):
        if is_valid_image(fn):
            candidates.append({"name": fn, "path": os.path.join(path, fn), "bytes": None})
    return candidates


def load_candidate_image(candidate):
    if candidate["bytes"] is not None:
        return load_image_from_bytes(candidate["bytes"])
    return Image.open(candidate["path"]).convert("RGB")


def get_candidate_bytes(candidate):
    if candidate["bytes"] is not None:
        return candidate["bytes"]
    with open(candidate["path"], "rb") as f:
        return f.read()


candidates = []
if source == "Local folder":
    candidates = prepare_local_candidates(folder_path)
    if folder_path and os.path.isdir(folder_path):
        st.success(f"Found {len(candidates)} image(s) in the folder.")
else:
    candidates = prepare_uploaded_candidates(uploaded_inputs or [])
    if uploaded_inputs:
        st.success(f"Loaded {len(candidates)} uploaded image(s).")

if candidates:
    with st.expander("Preview candidate images", expanded=False):
        cols = st.columns(3)
        for idx, candidate in enumerate(candidates):
            try:
                image = load_candidate_image(candidate)
                cols[idx % 3].image(
                    image,
                    caption=candidate["name"],
                    use_column_width=True,
                )
            except Exception as err:
                cols[idx % 3].write(f"Could not open {candidate['name']}: {err}")

st.markdown("---")
st.header("Match a reference image")

if not HAS_FACE_RECOGNITION:
    st.warning(
        "Face recognition package is not installed. Install `face_recognition` to enable person matching. "
        "Otherwise, the app will use visual similarity only."
    )

method = st.radio(
    "Matching method",
    ["Person face recognition", "Local visual similarity"],
    index=0 if HAS_FACE_RECOGNITION else 1,
)

if method == "Person face recognition":
    threshold = st.slider(
        "Face distance threshold (lower means closer match)",
        min_value=0.0,
        max_value=0.6,
        value=0.45,
        step=0.01,
    )
else:
    threshold = st.slider(
        "Hash distance threshold (lower means more exact)",
        min_value=0,
        max_value=50,
        value=20,
    )

max_matches = st.slider(
    "Maximum number of matches to show",
    min_value=1,
    max_value=20,
    value=10,
)

reference_file = st.file_uploader(
    "Upload one reference image to match against the selected images",
    type=["png", "jpg", "jpeg", "gif", "bmp", "webp"],
    accept_multiple_files=False,
)

if reference_file:
    if not candidates:
        st.warning("Select a local folder or upload image files/ZIP first.")
    else:
        try:
            reference_image = Image.open(BytesIO(reference_file.getbuffer())).convert("RGB")
            st.image(reference_image, caption="Reference image", use_column_width=True)
            matches = []

            if method == "Person face recognition":
                if not HAS_FACE_RECOGNITION:
                    st.error(
                        "face_recognition is not installed. Install it with `pip3 install face_recognition` "
                        "and restart the app."
                    )
                else:
                    reference_array = np.array(reference_image)
                    reference_encodings = face_recognition.face_encodings(reference_array)
                    if not reference_encodings:
                        st.error("No face found in the reference image.")
                    else:
                        reference_encoding = reference_encodings[0]
                        for candidate in candidates:
                            try:
                                candidate_image = load_candidate_image(candidate)
                                candidate_array = np.array(candidate_image)
                                candidate_encodings = face_recognition.face_encodings(candidate_array)
                                if not candidate_encodings:
                                    continue
                                distances = face_recognition.face_distance(candidate_encodings, reference_encoding)
                                min_distance = float(min(distances))
                                matches.append((candidate["name"], min_distance, candidate))
                            except Exception as err:
                                st.warning(f"Could not read {candidate['name']}: {err}")

                        matches.sort(key=lambda item: item[1])
                        matched_images = [item for item in matches if item[1] <= threshold]
                        if matched_images:
                            st.subheader(f"Found {len(matched_images)} images with the same person")
                        else:
                            st.warning(
                                "No matching faces were found below the selected threshold. "
                                "Try increasing the threshold slightly."
                            )
                            matched_images = matches[:max_matches]

                        matched_images = matched_images[:max_matches]
                        if matched_images:
                            cols = st.columns(3)
                            for idx, (name, distance, candidate) in enumerate(matched_images):
                                image = load_candidate_image(candidate)
                                cols[idx % 3].image(
                                    image,
                                    caption=f"{name} (distance={distance:.3f})",
                                    use_column_width=True,
                                )
                        else:
                            st.warning("No candidate images contained a detectable face.")

                        with st.expander("All face distances", expanded=False):
                            for name, distance, _ in matches:
                                st.write(f"{name}: distance {distance:.3f}")
            else:
                reference_hash = imagehash.phash(reference_image)
                hashed_reference = imagehash.dhash(reference_image)
                for candidate in candidates:
                    try:
                        candidate_image = load_candidate_image(candidate)
                        candidate_phash = imagehash.phash(candidate_image)
                        candidate_dhash = imagehash.dhash(candidate_image)
                        phash_distance = reference_hash - candidate_phash
                        dhash_distance = hashed_reference - candidate_dhash
                        distance = round((phash_distance + dhash_distance) / 2, 2)
                        matches.append((candidate["name"], distance, candidate))
                    except Exception as err:
                        st.warning(f"Could not read {candidate['name']}: {err}")

                matches.sort(key=lambda item: item[1])
                matched_images = [item for item in matches if item[1] <= threshold]
                if matched_images:
                    st.subheader(f"Found {len(matched_images)} matching image(s)")
                else:
                    st.warning(
                        "No exact matches were found below the threshold. Showing the closest candidates instead. "
                        "Try increasing the threshold to include more similar images."
                    )
                    matched_images = matches[:max_matches]

                matched_images = matched_images[:max_matches]
                cols = st.columns(3)
                for idx, (name, distance, candidate) in enumerate(matched_images):
                    image = load_candidate_image(candidate)
                    cols[idx % 3].image(
                        image,
                        caption=f"{name} (distance={distance})",
                        use_column_width=True,
                    )

                with st.expander("All candidate distances", expanded=False):
                    for name, distance, _ in matches:
                        st.write(f"{name}: distance {distance}")

        except Exception as err:
            st.error(f"Could not process the reference image: {err}")

st.markdown("---")

st.markdown(
    "Upload additional images to the local folder below, or use the uploaded images source instead."
)

uploaded_files = st.file_uploader(
    "Upload image(s) to the local folder",
    type=["png", "jpg", "jpeg", "gif", "bmp", "webp"],
    accept_multiple_files=True,
)

if uploaded_files:
    if not folder_path or not os.path.isdir(folder_path):
        st.warning("Enter a valid local folder path first so uploads can be saved.")
    else:
        saved = 0
        for uploaded_file in uploaded_files:
            save_path = os.path.join(folder_path, uploaded_file.name)
            with open(save_path, "wb") as out_file:
                out_file.write(uploaded_file.getbuffer())
            saved += 1
        st.success(f"Saved {saved} image(s) to {folder_path}.")
        st.info("Refresh the page to see newly added images.")
