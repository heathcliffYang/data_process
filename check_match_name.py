from data_process.file_utils.basic import TraverseDir, PathHandler
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predDir", type=str)

    args = parser.parse_args()

    fail_count = 0

    fail_list = []

    answer_pool = ['jJ28884', 'jD13339', 'ACE9116', 'w3931', 'BDF5678', 'jB61538', 'GSX3972', 'jA21473', 'jC21110', 'jB20612', 's705']
    answer_count = [0] * len(answer_pool)

    file_list = TraverseDir(args.predDir, '.jpg', skip='corners')
    for file_name in file_list:
        # print(file_name)
        file_name = file_name.split('_')
        # print(file_name)
        first_ans = file_name[1].replace('.jpg', '')
        second_ans = file_name[-1].replace('.jpg', '').replace('-', '')

        if second_ans not in answer_pool and second_ans != "":
            fail_count += 1
            fail_list.append(second_ans)



        for i, ans in enumerate(answer_pool):
            # print(i, second_ans)
            if second_ans == ans:
                # print(i, second_ans)
                answer_count[i] += 1

    print("Fail counts:", fail_count)
    print(answer_count)
    print(fail_list)
