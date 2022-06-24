import fire
import os


class Cli:
    def test(self, v):
        os.mkdir(v+'conf')

        with open('artsp/conf/config.py', 'r') as f:
            conf = f.read()

        with open('artsp/conf.txt', 'r') as f:
            conf_txt = f.read()

        with open(v+'conf/config.py', 'w') as a:
            a.write(conf_txt)

        path = os.path.abspath('./conf/config.py').replace('\\', '/')

        with open('artsp/conf/config.py', 'w') as f:
            f.writelines('import conf.config as conf\n')
            f.writelines(f"CONF_PATH = '{path}'\n")
            f.write(conf)

if __name__ == '__main__':
    fire.Fire(Cli)