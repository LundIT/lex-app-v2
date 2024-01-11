FROM python:3.8.5-slim-buster

# install all necessary packages
WORKDIR /app
RUN apt-get update && apt-get install -y curl gnupg2 wget apt-transport-https ca-certificates gnupg sudo&& \
    echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
        git \
        gcc \
        libpq-dev \
        wkhtmltopdf \
        rsync \
        g++ \
        wget \
        locales-all && \
    apt-get install -y google-chrome-stable && \
    wget http://ftp.de.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.7_all.deb -P /tmp && \
    ACCEPT_EULA=Y apt install -y \
        /tmp/ttf-mscorefonts-installer_3.7_all.deb && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# copy the repository and install all requirements
ADD ./requirements.txt /app/DjangoProcessAdminGeneric/requirements.txt
ADD ./build/download_chromedriver.py /app/DjangoProcessAdminGeneric/build/download_chromedriver.py
RUN pip install --no-cache-dir -r /app/DjangoProcessAdminGeneric/requirements.txt
RUN python3 /app/DjangoProcessAdminGeneric/build/download_chromedriver.py

# Install Google Cloud SDK to get the gsutil tool
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-cli -y

ADD . /app/DjangoProcessAdminGeneric
WORKDIR /app/DjangoProcessAdminGeneric

RUN chmod +x /app/DjangoProcessAdminGeneric/build/container_startup.sh && \
    chmod +x /app/DjangoProcessAdminGeneric/build/wait-for-it.sh && \
    chmod +x /app/DjangoProcessAdminGeneric/build/start_streamlit.sh && \
    chmod +x /app/DjangoProcessAdminGeneric/build/start_worker.sh

WORKDIR /app/DjangoProcessAdminGeneric/

EXPOSE 7000

CMD /app/DjangoProcessAdminGeneric/build/container_startup.sh
