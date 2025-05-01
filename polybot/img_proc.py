import random
from pathlib import Path
from matplotlib.image import imread, imsave


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):
        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2
        result = []

        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j - 1] - row[j]))

            self.data[i] = res

    def rotate(self):
        transposed = list(zip(*self.data))  # *self.data unpacks all the rows into the zip function
        transposed = [list(row) for row in transposed]
        for row in transposed:
            row.reverse()  # in order to rotate clockwise, not counterclockwise

        self.data = transposed  # save the rotated image

    def salt_n_pepper(self):
        for i, row in enumerate(self.data):
            for j, _ in enumerate(row):
                ran_num = random.random()
                if ran_num < 0.2:
                    self.data[i][j] = 255
                elif ran_num > 0.8:
                    self.data[i][j] = 0

        # for row in range(len(self.data)):
        #     for col in range(len(self.data[row])):
        #         ran_num = random.random()
        #         if ran_num < 0.2:
        #             self.data[row][col] = 255
        #         elif ran_num > 0.8:
        #             self.data[row][col] = 0

    def concat(self, other_img, direction='horizontal'):
        # horizontal - side by side - both images must have the same number of rows
        if direction == 'horizontal':
            min_height = min(len(self.data), len(other_img.data))
            self.data = [row1[:min(len(row1), len(row2))] + row2[:min(len(row1), len(row2))]
                         for row1, row2 in zip(self.data[:min_height], other_img.data[:min_height])]
        elif direction == 'vertical':
            # vertical - 1 below the other - both images must have the same number of columns
            min_width = min(len(self.data[0]), len(other_img.data[0]))
            self.data = [row[:min_width] for row in self.data] + [row[:min_width] for row in other_img.data]

        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")

    def segment(self):
        for i, row in enumerate(self.data):
            for j, val in enumerate(row):
                self.data[i][j] = 255 if val > 100 else 0

        return self
