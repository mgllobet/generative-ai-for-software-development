import threading

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self, max_size=None):
        self.head = None
        self.size = 0
        self.max_size = max_size  # Maximum size limit for the linked list
        self.lock = threading.Lock()  # Lock for concurrency control

    def append(self, data):
        # Validate input data
        if len(data) > 1000:  # Example: Limit data size to prevent excessively large payloads
            raise ValueError("Data size exceeds maximum limit")

        with self.lock:
            # Rate limiting mechanism can be implemented here
            if self.max_size is not None and self.size >= self.max_size:
                raise ValueError("Linked list is full")

            new_node = Node(data)
            if self.head is None:
                self.head = new_node
            else:
                last = self.head
                while last.next:
                    last = last.next
                last.next = new_node
            self.size += 1

    def print_list(self):
        current = self.head
        while current:
            print(current.data, end=" ")
            current = current.next

# Example usage
list = LinkedList(max_size=1000)  # Set maximum size limit
list.append("Data 1")
list.append("Data 2")
list.print_list()
