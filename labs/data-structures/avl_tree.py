import threading

class AVLNode:
    # Constructor to initialize an AVL tree node.
    def __init__(self, key):
        self.left = None    # Pointer to the left child, initially None.
        self.right = None   # Pointer to the right child, initially None.
        self.val = key      # The value/key of the node.
        self.height = 1     # The height of the node, initially 1 since it's a leaf when created.

class AVLTree:
    # Constructor to initialize an AVL tree.
    def __init__(self):
        self.root = None        # The root node of the tree, initially None.
        self.tree_lock = threading.Lock()  # A lock to ensure thread-safe modifications.

    # Public method to insert a key into the AVL tree.
    def insert(self, key):
        with self.tree_lock:  # Acquire the lock to ensure exclusive access for the operation.
            self.root = self._insert(self.root, key)  # Start insertion from the root.

    # Internal recursive method to handle the insertion logic.
    def _insert(self, node, key):
        if not node:
            return AVLNode(key)  # Base case: return a new node if we reach a leaf position.

        # Recursive case: navigate to the correct position in the tree.
        if key < node.val:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)

        # After insertion, update the height of the current node.
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # Check and fix the balance of the tree if needed.
        return self._rebalance(node, key)

    # Method to delete a node with the specified key.
    def delete(self, key):
        with self.tree_lock:  # Acquire the lock to ensure exclusive access for the operation.
            self.root = self._delete(self.root, key)  # Start deletion from the root.

    # Internal recursive method to handle the deletion logic.
    def _delete(self, node, key):
        if not node:
            return node  # Base case: if key isn't found, do nothing.

        # Recursive deletion according to the key comparison.
        if key < node.val:
            node.left = self._delete(node.left, key)
        elif key > node.val:
            node.right = self._delete(node.right, key)
        else:
            # Handling the node with two children or one/no children.
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Finding the smallest node in the right subtree to replace the current node.
            temp = self._get_min_value_node(node.right)
            node.val = temp.val
            node.right = self._delete(node.right, temp.val)

        # Update the height of the node and rebalance it.
        return self._rebalance(node, None)

    # Helper function to get the node with the minimum value (used in deletion).
    def _get_min_value_node(self, node):
        current = node
        while current and current.left is not None:
            current = current.left
        return current

    # Public method to search for a key in the tree.
    def search(self, key):
        with self.tree_lock:
            return self._search(self.root, key)  # Start searching from the root.

    # Internal recursive method to handle the search logic.
    def _search(self, node, key):
        # Base case: return the node if found, or None if not found.
        if not node or node.val == key:
            return node

        # Navigate to the left or right subtree based on the key comparison.
        if key < node.val:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    # Method to print all nodes in the tree in in-order sequence.
    def print_in_order(self):
        output = []
        self._print_in_order(self.root, output)
        return output

    # Internal recursive method to collect values in in-order sequence.
    def _print_in_order(self, node, output):
        if node:
            self._print_in_order(node.left, output)
            output.append(node.val)
            self._print_in_order(node.right, output)

    # Utility method to get the height of a node.
    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    # Utility method to calculate the balance factor of a node.
    def _get_balance(self, node):
        if not node:
            return 