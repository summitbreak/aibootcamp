ARG PLATFORM=linux/amd64
FROM --platform=$PLATFORM public.ecr.aws/lambda/python:3.12

# Install Java 17 and dependencies
RUN yum install -y \
    java-17-amazon-corretto-devel \
    wget \
    tar \
    gzip \
    zip \
    && yum clean all

# Install Maven
ARG MAVEN_VERSION=3.9.6
RUN wget https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz -P /tmp && \
    tar -xzf /tmp/apache-maven-${MAVEN_VERSION}-bin.tar.gz -C /opt && \
    ln -s /opt/apache-maven-${MAVEN_VERSION} /opt/maven && \
    rm /tmp/apache-maven-${MAVEN_VERSION}-bin.tar.gz

# Set Java and Maven environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto
ENV MAVEN_HOME=/opt/maven
ENV PATH=$JAVA_HOME/bin:$MAVEN_HOME/bin:$PATH

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -t /var/task/

# Copy function code
COPY lambda_handler.py /var/task/

CMD ["lambda_handler.lambda_handler"]