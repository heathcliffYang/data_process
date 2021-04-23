from data_process.file_utils.basic import TraverseDir, PathHandler
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predDir", type=str)

    args = parser.parse_args()

    count = 0

    file_list = TraverseDir(args.predDir, '.jpg', skip='corners')
    for file_name in file_list:
        # print(file_name)
        file_name = file_name.split('_')
        # print(file_name)
        first_ans = file_name[1].replace('.png', '')
        second_ans = file_name[3].replace('.jpg', '').replace('-', '')

        if first_ans != second_ans:
            count += 1
            print(file_name[0], first_ans, second_ans)
    print("Different counts:", count)
