#include <iostream>
#include<sys/socket.h>
#include "Server.h"
#include "Client.h"



int main() {

    Server server(1);

    server.start();


}
