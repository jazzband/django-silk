
jdk-install:
  pkg.installed:
    - name: openjdk-7-jdk

elasticsearch:
  pkg:
    - installed
    - sources:
      - elasticsearch: https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.deb
  service.running:
    - enable: True
    - require:
      - pkg: elasticsearch
      - file: /var/data/elasticsearch
      - file: /var/log/elasticsearch

/var/data/elasticsearch:
  file.directory:
    - user: elasticsearch
    - group: elasticsearch
    - makedirs: true
    - require:
      - pkg: elasticsearch

/var/log/elasticsearch:
  file.directory:
    - user: elasticsearch
    - group: elasticsearch
    - makedirs: true
    - require:
      - pkg: elasticsearch
