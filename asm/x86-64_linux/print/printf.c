/*
	Ember ASM: Debug Print Float

	Reference: https://www.geeksforgeeks.org/convert-floating-point-number-string/

	Written By: Ryan Smith
*/
#ifdef BUFFER_CAPACITY
	#undef BUFFER_CAPACITY
#endif
#define BUFFER_CAPACITY 64

#include <unistd.h>

void PRINTF(double value)
{
	int bufferSize = 1;
	char buffer[BUFFER_CAPACITY];
	buffer[BUFFER_CAPACITY - 1] = '\n';
	int isNegative = value < 0;
	/// long long int topHalf = (long long int)value;
	/// int isNegative = topHalf < 0;
	/// unsigned long long int bottomHalf = (unsigned long long int)((value - (double)topHalf) * 10000000);

	// Write: 6 decimal places
	// Write: separator
	buffer[BUFFER_CAPACITY - 1 - (bufferSize++)] = '.';
	// Write: top of float
	// Write: sign
	if (isNegative)
		buffer[BUFFER_CAPACITY - 1 - (bufferSize++)] = '-';
	write(1, &buffer[BUFFER_CAPACITY - bufferSize], bufferSize);
}
