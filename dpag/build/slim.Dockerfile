######################## STAGE 1 ################################
FROM python:3.8.5-slim as builder
# install all necessary packages
WORKDIR /app/DjangoProcessAdminGeneric
RUN apt-get update && apt-get install -y git
ADD . /app/DjangoProcessAdminGeneric

########### configure venv ##########
RUN pip3 install virtualenv
ENV VIRTUAL_ENV=/app/DjangoProcessAdminGeneric/venv
RUN python3 -m virtualenv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#####################################
RUN pip install --no-cache-dir -r /app/DjangoProcessAdminGeneric/requirements.txt

######################## STAGE 2 ################################
FROM python:3.8.5-slim
RUN apt-get update && apt-get install -y git rsync

WORKDIR /app/DjangoProcessAdminGeneric
COPY --from=builder /app/DjangoProcessAdminGeneric /app/DjangoProcessAdminGeneric

########### configure venv ##########
ENV VIRTUAL_ENV=/app/DjangoProcessAdminGeneric/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#####################################

RUN chmod +x /app/DjangoProcessAdminGeneric/build/container_startup.sh && \
    chmod +x /app/DjangoProcessAdminGeneric/build/wait-for-it.sh && \
    chmod +x /app/DjangoProcessAdminGeneric/build/start_streamlit.sh


WORKDIR /app/DjangoProcessAdminGeneric/

EXPOSE 7000

CMD /app/DjangoProcessAdminGeneric/build/container_startup.sh
