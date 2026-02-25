FROM  --platform=linux/amd64  public.ecr.aws/lambda/python:3.12 AS builder

# Install Java 21 (Amazon Corretto) and dependencies
RUN yum install -y \
    java-21-amazon-corretto-devel \
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

# Install Python packages into layer (add any packages you need here)
RUN pip install --upgrade pip && \
    pip install \
        boto3 \
        requests \
    -t /layer/python/lib/python3.12/site-packages/

# Copy Java into layer structure (/opt is where Lambda extracts layers)
RUN mkdir -p /layer/java && \
    cp -r /usr/lib/jvm/java-21-amazon-corretto /layer/java/jdk

# Copy Maven into layer structure
RUN mkdir -p /layer/maven && \
    cp -r /opt/maven /layer/maven/maven

# Create an env vars script that your Lambda handler can source
RUN mkdir -p /layer/bin && \
    cat > /layer/bin/set-java-env.sh <<'EOF'
#!/bin/bash
export JAVA_HOME=/opt/java/jdk
export MAVEN_HOME=/opt/maven/maven
export PATH=$JAVA_HOME/bin:$MAVEN_HOME/bin:$PATH
EOF
RUN chmod +x /layer/bin/set-java-env.sh

# Package everything
RUN cd /layer && zip -r /layer.zip .

FROM scratch
COPY --from=builder /layer.zip /layer.zip

# Command to run the Lambda function
CMD ["lambda_handler.lambda_handler"]
