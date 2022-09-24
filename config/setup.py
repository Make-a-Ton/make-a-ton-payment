import pathlib
import subprocess


def run():
    pathlib.Path("../static").mkdir(exist_ok=True, parents=True)
    subprocess.Popen("python -m venv venv", cwd="../").wait()
    subprocess.Popen(". venv/bin/activate && "
                     "pip install -r requirements.txt", cwd="../").wait()

    from config.variables import set_up

    config = set_up()

    db = config["database"]

    subprocess.Popen("docker run --rm  --name  postgres "
                     f"-p {db['port']}:{db['port']} "
                     f"-e POSTGRES_USER={db['user']} "
                     f"-e POSTGRES_PASSWORD={db['password']} "
                     f"-e POSTGRES_DB={db['name']} "
                     f"-d postgres").wait()

    subprocess.Popen("alembic upgrade head", cwd="../").wait()


if __name__ == "__main__":
    run()
