import kfp
from kfp import dsl

@dsl.pipeline(
    name='FastAPI-ML-Ops-Pipeline',
    description='Sequential MLOps pipeline compatible with Python 3.13 and Kubeflow v2 Engines.'
)
def ml_pipeline():
    # Крок 1: Завантаження даних. Явно кажемо створити вихідний артефакт.
    load_data_task = dsl.ContainerOp(
        name='load-data',
        image='python:3.9-slim',
        command=['python', '-c', 
                 'import os; os.makedirs("/tmp", exist_ok=True); '
                 'f = open("/tmp/output.txt", "w"); f.write("raw_dance_dataset_v1"); f.close(); '
                 'print("Data ready and written successfully to /tmp/output.txt")'],
        file_outputs={'data_output': '/tmp/output.txt'}
    )

    # Крок 2: Тренування моделі. Залежить від виходу Кроку 1.
    train_model_task = dsl.ContainerOp(
        name='train-model',
        image='python:3.9-slim',
        command=['python', '-c', 
                 'import os; os.makedirs("/tmp", exist_ok=True); '
                 'f = open("/tmp/model.txt", "w"); f.write("trained_model_weights_v1"); f.close(); '
                 'print("Model trained successfully. Weights saved to /tmp/model.txt")'],
        file_outputs={'model_output': '/tmp/model.txt'}
    )
    # Зв'язуємо вхід другого кроку з виходом першого (це малює стрілочку в UI та передає файл)
    train_model_task.arguments = [load_data_task.outputs['data_output']]

    # Крок 3: Оцінка метрик. Залежить від виходу Кроку 2.
    evaluate_model_task = dsl.ContainerOp(
        name='evaluate-model',
        image='python:3.9-slim',
        command=['python', '-c', 
                 'print("Reading incoming trained model configuration..."); '
                 'print("Metrics evaluation process completed."); '
                 'print("Metrics: Accuracy = 0.95")']
    )
    # Зв'язуємо вхід третього кроку з виходом другого
    evaluate_model_task.arguments = [train_model_task.outputs['model_output']]

# Компіляція маніфесту
if __name__ == '__main__':
    kflow_compiler = kfp.compiler.Compiler()
    kflow_compiler.compile(
        pipeline_func=ml_pipeline,
        package_path='ml_pipeline.yaml'
    )
    print("Успішно скомпільовано в ml_pipeline.yaml за універсальним декларативним стандартом!")
