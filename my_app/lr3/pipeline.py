import kfp
from kfp import dsl

# Використовуємо ContainerOp для гарантованої стабільності
def ml_pipeline():
    # Крок 1: Завантаження даних
    data_task = dsl.ContainerOp(
        name='load-data',
        image='python:3.9-slim',
        command=['python', '-c', 'print("Data ready")'],
        file_outputs={'data_output': '/tmp/output.txt'}
    )

    # Крок 2: Навчання (залежить від виходу попереднього кроку)
    train_task = dsl.ContainerOp(
        name='train-model',
        image='python:3.9-slim',
        command=['python', '-c', 'print("Model trained")'],
        file_outputs={'train_output': '/tmp/output.txt'}
    )

    # Крок 3: Оцінка
    eval_task = dsl.ContainerOp(
        name='evaluate-model',
        image='python:3.9-slim',
        command=['python', '-c', 'print("Metrics 0.95")']
    )
# Компіляція пайплайну
if __name__ == '__main__':
    # Використовуємо офіційний компілятор KFP
    kfp.compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path='ml_pipeline.yaml'
    )
    print("Успішно скомпільовано в ml_pipeline.yaml!")