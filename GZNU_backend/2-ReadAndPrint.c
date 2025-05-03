// Copyright (c) 2025 陈中旭
// License MIT
// Date: 2025.05.03
// Author: nanachiy(393744534@qq.com)
// Calculate frame loss rates of files through comparing VDIF headers.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define BUFFER_SIZE 8256
#define NUM_PKT_SEC 250000

// Print data in hexacdamical formart
void print_hex_ascii(const char *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        printf("%02X ", (unsigned char)data[i]);
        if ((i + 1) % 16 == 0) printf(" | ");
        if ((i + 1) % 16 == 0 || i == len - 1) {
            for (size_t j = (i - (i % 16)); j <= i; j++) {
                if (data[j] >= 32 && data[j] <= 126)
                    printf("%c", data[j]);
                else
                    printf(".");
            }
            printf("\n");
        }
    }
}
 
// Main program
int main(int argc, char *argv[]) {
    // Initializing
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file.bin>\n", argv[0]);
        return 1;
    }

    FILE *input_file = fopen(argv[1], "rb");
    if (!input_file) {
        perror("fopen failed");
        return 1;
    }

    ssize_t recv_len;
    char buffer[BUFFER_SIZE];
    int packet_count = 0;
    int frame_count = 0;
    int frame_start, time_start, frame_end, time_end;
    int32_t header[8];
    int sec_ref_ep;
    int ref_ep;
    recv_len = 8256;
    
    while (fread(buffer, 1, recv_len, input_file) == recv_len) {
        ++packet_count;
        // printf("\n=== Packet %d (Length: %zd) ===\n", ++packet_count, recv_len);
        if (packet_count == 1){
        memcpy(header, buffer, sizeof(header));
        sec_ref_ep = header[0] & ((1 << 30) - 1);
        ref_ep = (header[1] >> 24) & ((1 << 6) - 1);
        
        // Get the second the frame number of the 1st packet
        struct tm tm = {0};
        tm.tm_year = 2000 + (ref_ep / 2) - 1900;
        tm.tm_mon = 1 + (ref_ep & 1) * 6 - 1;
        tm.tm_mday = 1;
        time_t timestamp = mktime(&tm) + sec_ref_ep;
        char time_str[26];
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&timestamp));
            frame_start = header[1] & ((1 << 24) - 1);
            time_start = sec_ref_ep;
        }

        // Print data contents
        // printf("\n--- Data Content ---\n");
        // print_hex_ascii(buffer + 32, recv_len - 32);
        
    }

    // Get the second the frame number of the last packet
    memcpy(header, buffer, sizeof(header));
    sec_ref_ep = header[0] & ((1 << 30) - 1);
    ref_ep = (header[1] >> 24) & ((1 << 6) - 1);
        
    struct tm tm = {0};
    tm.tm_year = 2000 + (ref_ep / 2) - 1900;
    tm.tm_mon = 1 + (ref_ep & 1) * 6 - 1;
    tm.tm_mday = 1;
    time_t timestamp = mktime(&tm) + sec_ref_ep;
    char time_str[26];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&timestamp));

    fclose(input_file);

    frame_end = header[1] & ((1 << 24) - 1);
    time_end = sec_ref_ep;

    printf("%d\n", time_start);
    printf("%d\n", time_end);
    printf("%d\n", frame_start);
    printf("%d\n", frame_end);

    // Calculate and print loss rate
    int n_total_frame = (time_end - time_start)*NUM_PKT_SEC + (frame_end - frame_start + 1);
    printf("Pkt: %d\n", packet_count);
    printf("Frame: %d\n", n_total_frame);
    printf("Loss Rate: %f%%\n", 100*(float)(n_total_frame - packet_count)/(float)(n_total_frame));
    return 0;
}
