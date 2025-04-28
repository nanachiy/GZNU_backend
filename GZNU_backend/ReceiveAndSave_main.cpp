//1.Programe1:读取UDP数据并存储 参数1：循环条数 参数2：

#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <time.h>
#include <thread>
#include <string.h>
#include <string>
#include <queue>
#include <unistd.h>
#include <iostream>

// #define UDP_IP "10.17.16.12"
// #define UDP_PORT 17201
#define BUFFER_SIZE 8256
#define BATCH_SIZE 1000
// #define FILE_PATH "storage.bin_"

std::queue<char*> data_queue;
bool shutdown_flag = false;
// int n_write = 250*60*5;
char batch[BUFFER_SIZE*BATCH_SIZE];
int size_file = 2500;

void udp_receiver(int n_write, char *UDP_IP, int UDP_PORT) {
    int sockfd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket creation failed");
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(UDP_IP);
    server_addr.sin_port = htons(UDP_PORT);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind failed");
        close(sockfd);
    }

    for (int i = 0; i < n_write; i++) {  // 持续接收，可通过Ctrl+C终止
        char* buffer = new char[BUFFER_SIZE*BATCH_SIZE];
        for(int j = 0; j < BATCH_SIZE; j++){
            recvfrom(sockfd, &buffer[BUFFER_SIZE*j], BUFFER_SIZE, 0,
                (struct sockaddr *)&client_addr, &client_addr_len);
        }
        data_queue.push(buffer);
    }
    close(sockfd);
    shutdown_flag = true;
}


void file_writer(int n_file, const char *FILE_PATH) {
    std::string filename_s = FILE_PATH + std::to_string(n_file);
    const char *filename = filename_s.c_str();

    // printf("%s", filename);
    FILE *output_file = fopen(filename, "wb");

    // if (!output_file) {
    //     perror("fopen failed");
    // }

    int i_write = 0;
    while (i_write < size_file && (!data_queue.empty() || !shutdown_flag)){
        if(!data_queue.empty()){
            fwrite(data_queue.front(), 1, BUFFER_SIZE*BATCH_SIZE, output_file);
            delete[] data_queue.front();
            data_queue.pop();
            ++i_write;
        }
    }
    fclose(output_file);
}


int main(int argc, char *argv[]) {
    clock_t start, end;
    double time_used;
    start = clock();

    if (argc != 5) {
        printf("[Main] Number of arguments is not correct.");
        return 1;
    }

    int n_file = 0;
    int n_write = atoi(argv[1]);
    char *FILE_PATH = argv[2];
    char *UDP_IP = argv[3];
    int UDP_PORT = atoi(argv[4]);

    while(!shutdown_flag || !data_queue.empty()){

        std::thread writer_thread(file_writer, n_file, FILE_PATH);
        if(n_file == 0){
            std::thread receiver_thread(udp_receiver, n_write, UDP_IP, UDP_PORT);
            receiver_thread.detach();
        }

        writer_thread.join();
        printf("Writer_thread %s%d is done.\n", FILE_PATH, n_file);
        ++ n_file;
    }


    printf("[Main] All threads stopped\n");
    end = clock();

    time_used = ((double)(end - start))/CLOCKS_PER_SEC;
    printf("[Main] Time Used: %f seconds\n", time_used);

    return 0;
}
