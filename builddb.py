import sys
sys.path.append("irdata")

import yaml

import irdata.load

if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)
    irdata.load.main(config)
