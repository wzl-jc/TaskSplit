import yaml
from TaskClassDict import task_class_dict as td


def yaml_to_dict(cont):
    task_dag_data = yaml.safe_load(cont)
    result_dict = {}
    for key, values in task_dag_data.items():
        result_key = td[key]
        result_dict[result_key] = []
        if values is None:
            continue
        for value in values:
            result_value = td[value]
            result_dict[result_key].append(result_value)
    return result_dict

# f = open("register_task/task_example.yaml", 'r', encoding='utf-8')
# cont = f.read()
# task_dag_data = yaml.safe_load(cont)
# result_dict = {}
# for key, values in task_dag_data.items():
#     result_key = td[key]
#     result_dict[result_key] = []
#     if values == None:
#         continue
#     for value in values:
#         result_value = td[value]
#         result_dict[result_key].append(result_value)
# print(result_dict)

# task_dag = {
#         td['Preprocessing']: [],
#         td['Detection']: [td['Preprocessing']],
#         td['HelmetDetection']: [td['Detection']],
#         td['FaceDetection']: [td['Detection']],
#         td['HumanPoseEstimation']: [td['FaceDetection']],
#     }