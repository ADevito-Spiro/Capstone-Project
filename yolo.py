from ultralytics import YOLO
import cv2, math, numpy as np, threading, queue

chessboard_size = (7, 7)

# Start the webcam, if using Windows use this
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(3, 540)
cap.set(4, 720)

# Load the YOLO model
model = YOLO("yolo-Weights/bestBig.pt")

def map_to_board(x, y, corners):
    board_positions = {}
    square_centers = {}

    for row in range(chessboard_size[1] - 1):
        for col in range(chessboard_size[0] - 1):
            idx_tl = row * chessboard_size[0] + col
            idx_tr = idx_tl + 1
            idx_bl = idx_tl + chessboard_size[0]
            idx_br = idx_bl + 1

            pts = [corners[idx_tl], corners[idx_tr], corners[idx_bl], corners[idx_br]]
            center = np.mean(pts, axis=0)

            board_positions[(col, row)] = f"{chr(65 + col)}{row + 1}"

            square_centers[(col, row)] = center

    closest_square = min(
        square_centers.keys(),
        key=lambda pos: (square_centers[pos][0] - x) ** 2 + (square_centers[pos][1] - y) ** 2
    )
    return board_positions[closest_square]

def detect_pieces(detected_pieces, img, corners):
    results = model(img, stream=True)
    temp_detected_pieces = {}

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 3)
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            class_name = model.names[cls]
            label = f"{class_name}: {confidence * 100:.2f}%"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            piece_x, piece_y = (x1 + x2) // 2, (y1 + y2) // 2

            board_pos = map_to_board(piece_x, piece_y, corners)
            if board_pos:
                temp_detected_pieces[board_pos] = class_name
                print(f"Detected {class_name} at pixel ({piece_x}, {piece_y}) -> board square: {board_pos}")


    detected_pieces.clear()
    detected_pieces.update(temp_detected_pieces)
    return img

def detect_board(img, board_corners):
    # Convert to grayscale once
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply contrast enhancement and blur
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Attempt to find chessboard corners
    found, corners = cv2.findChessboardCorners(
        gray, chessboard_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK
    )

    if found:
        corners = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )
        corners = corners.reshape(-1, 2)

        # Draw corner grid and label each square
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        color = (0, 255, 255)  # Yellow

        for row in range(chessboard_size[1] - 1):
            for col in range(chessboard_size[0] - 1):
                # Get the 4 corners of the current square
                top_left = corners[row * chessboard_size[0] + col]
                top_right = corners[row * chessboard_size[0] + col + 1]
                bottom_left = corners[(row + 1) * chessboard_size[0] + col]
                bottom_right = corners[(row + 1) * chessboard_size[0] + col + 1]

                # Compute the center of the square
                center_x = int((top_left[0] + top_right[0] + bottom_left[0] + bottom_right[0]) / 4)
                center_y = int((top_left[1] + top_right[1] + bottom_left[1] + bottom_right[1]) / 4)

                # Compute square index (optional: customize how it’s numbered)
                square_index = row * (chessboard_size[0] - 1) + col
                cv2.putText(img, str(square_index), (center_x - 10, center_y + 5), font, font_scale, color, thickness)

        # Update board_corners as before
        board_corners.clear()
        board_corners.extend(corners)

    return img

def main(yolo_queue):
    previous_pieces = {}
    detected_pieces = {}
    board_corners = []
    corners_locked = False

    while True:
        success, img = cap.read()
        if not success:
            continue

        shared_img = img.copy()

        # Lock in corners only once
        if not corners_locked:
            temp_corners = []
            temp_img = detect_board(shared_img.copy(), temp_corners)
            if temp_corners:
                board_corners.extend(temp_corners)
                corners_locked = True

        if corners_locked:
            shared_img = detect_pieces(detected_pieces, shared_img, board_corners)

        if detected_pieces != previous_pieces:
            yolo_queue.put(detected_pieces.copy())
            previous_pieces = detected_pieces.copy()

        # Optionally draw locked-in corners for reference
        if len(board_corners) == chessboard_size[0] * chessboard_size[1]:
            font = cv2.FONT_HERSHEY_SIMPLEX
            square_index = 1

            # Highlight these path coordinates (col, row)
            custom_path = [
                (0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
                (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5)
            ]

            for row in range(chessboard_size[1] - 1):
                for col in range(chessboard_size[0] - 1):
                    i = row * chessboard_size[0] + col

                    top_left = board_corners[i]
                    top_right = board_corners[i + 1]
                    bottom_left = board_corners[i + chessboard_size[0]]
                    bottom_right = board_corners[i + chessboard_size[0] + 1]

                    pts = np.array([top_left, top_right, bottom_right, bottom_left], np.int32).reshape((-1, 1, 2))

                    # Highlight path tiles in yellow
                    if (row, col) in custom_path:
                        cv2.fillPoly(shared_img, [pts], color=(0, 255, 255))  # Yellow fill

                    # Optional: still draw green outline
                    cv2.polylines(shared_img, [pts], isClosed=True, color=(0, 255, 0), thickness=1)

                    # Draw square index
                    center_x = int((top_left[0] + top_right[0] + bottom_left[0] + bottom_right[0]) / 4)
                    center_y = int((top_left[1] + top_right[1] + bottom_left[1] + bottom_right[1]) / 4)
                    cv2.putText(shared_img, str(square_index), (center_x - 10, center_y + 5), font, 0.5, (0, 255, 0), 1)
                    square_index += 1

        cv2.imshow("Chessboard & Pieces Detection", shared_img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            board_corners.clear()
            corners_locked = False
            print("Board detection reset.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    yolo_queue = queue.Queue()
    main(yolo_queue)