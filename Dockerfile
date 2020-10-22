# Base image
FROM ubuntu:18.04

# Environment vars
ENV DEBIAN_FRONTEND="noninteractive" \
    ANALYZER_IDENTIFIER="" \
    JDK_FILE="openjdk-12_linux-x64_bin.tar.gz" \
    WKH_FILE="wkhtmltox_0.12.1.4-2.bionic_amd64.deb"

ENV JDK_URL="https://download.java.net/java/GA/jdk12/GPL/${JDK_FILE}" \
    WKH_URL="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.1.4-2/${WKH_FILE}"

# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run
RUN apt update -y && apt install -y \
    build-essential \
    git \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    locales \
    sqlite3 \
    fontconfig-config \
    libjpeg-turbo8 \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    fontconfig \
    xfonts-75dpi \
    xfonts-base \
    python3.6 \
    python3-dev \
    python3-pip \
    wget \
    android-tools-adb

# Set locales
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# Install Wkhtmltopdf
RUN wget --quiet -O /tmp/${WKH_FILE} "${WKH_URL}" && \
    dpkg -i /tmp/${WKH_FILE} && \
    apt-get install -f -y --no-install-recommends && \
    ln -s /usr/local/bin/wkhtmltopdf /usr/bin && \
    rm -f /tmp/${WKH_FILE}

# Install OpenJDK12
RUN wget --quiet "${JDK_URL}" && \
    tar zxf "${JDK_FILE}" && \
    rm -f "${JDK_FILE}"
ENV JAVA_HOME="/jdk-12"
ENV PATH="$JAVA_HOME/bin:$PATH"

#Fonts
COPY /docker/winFonts /usr/share/fonts/
WORKDIR /usr/share/fonts/winFonts
RUN chmod -R 755 /usr/share/fonts && \
    mkfontscale && \
    mkfontdir && \
    fc-cache -fv

WORKDIR /root/Mobile-Security-Framework-MobSF
COPY ./requirements.txt .

# Install Requirements
RUN pip3 install --upgrade wheel && \
    pip3 wheel --wheel-dir=yara-python --build-option="build" --build-option="--enable-dex" git+https://github.com/VirusTotal/yara-python.git@v3.11.0 && \
    pip3 install --no-index --find-links=yara-python yara-python && \
    rm -rf yara-python
RUN pip3 install --quiet --no-cache-dir -r requirements.txt

# Cleanup
RUN \
    apt remove -y \
        git \
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        python3-dev \
        wget && \
    apt clean && \
    apt autoclean && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* > /dev/null 2>&1


# Add apktool working path  log dir
RUN mkdir -p /root/.local/share/apktool/framework \
    mkdir -p /root/Mobile-Security-Framework-MobSF/logs


# Expose MobSF Port
EXPOSE 8000
# MobSF Proxy
EXPOSE 1337

# Run MobSF
CMD bash /root/Mobile-Security-Framework-MobSF/docker/mobsf-start.sh
