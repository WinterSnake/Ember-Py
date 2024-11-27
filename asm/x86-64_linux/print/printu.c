/*
	Ember ASM: Debug Print UInt

	Written By: Ryan Smith
*/
#ifdef BUFFER_CAPACITY
	#undef BUFFER_CAPACITY
#endif
#define BUFFER_CAPACITY 32

#include <unistd.h>

void PRINTU(unsigned long long int value)
{
	int bufferSize = 1;
	char buffer[BUFFER_CAPACITY];
	buffer[BUFFER_CAPACITY - 1] = '\n';
	// Write: value
	do
	{
		char output = value % 10 + '0';
		buffer[BUFFER_CAPACITY - 1 - (bufferSize++)] = output;
		value /= 10;
	} while(value);
	write(1, &buffer[BUFFER_CAPACITY - bufferSize], bufferSize);
}
