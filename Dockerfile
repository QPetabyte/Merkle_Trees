#Start with the standard Nginx image from DockerHub
FROM python:3.9-slim-bullseye
# Dockerfile author
LABEL Qwerty Petabyte (qpetabyte@kringlecon.com)
# update, install prerequisites, and add a user
RUN apt-get update && apt-get upgrade -y && pip install eth_typing hexbytes web3 && \
    useradd -m -s /bin/bash mt_user
USER mt_user
# copy in the code
COPY merkle_tree.py /home/mt_user/merkle_tree.py
WORKDIR /home/mt_user
CMD ["/bin/bash"]
