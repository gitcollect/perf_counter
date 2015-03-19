CC = gcc
TARGET1 = event_open_default
TARGET2 = event_open_raw
RM = rm -rf

all: $(TARGET1) $(TARGET2)

$(TARGET1): $(TARGET1).c
	$(CC) -o $(TARGET1) $(TARGET1).c

$(TARGET2): $(TARGET2).c
	$(CC) -o $(TARGET2) $(TARGET2).c

clean:
	$(RM) $(TARGET1) $(TARGET2)
