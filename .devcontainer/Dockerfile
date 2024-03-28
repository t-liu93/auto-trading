FROM debian:bookworm-slim

RUN apt update
RUN apt upgrade

RUN apt install -y git nano curl wget python3 python-is-python3 python3-venv python3-dev gcc build-essential 

# dependencies
RUN mkdir -p /root/temp
WORKDIR /root/temp
RUN wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
RUN tar -xzf ta-lib-0.4.0-src.tar.gz
WORKDIR /root/temp/ta-lib
RUN ./configure --prefix=/usr
RUN make && make install
WORKDIR /root
RUN rm -rf /root/temp

# not necessary
RUN apt install -y zsh locales locales-all zsh-autosuggestions zsh-syntax-highlighting
RUN chsh -s /usr/bin/zsh root
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
RUN sed -i 's\robbyrussell\agnoster\g' $HOME/.zshrc
RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
RUN sed -i 's\plugins=(git)\plugins=(git zsh-autosuggestions)\g' $HOME/.zshrc
RUN echo "source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
