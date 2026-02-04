class LayoutEngine:
    def __init__(self):
        pass

    def build_layout(self, elements, ocr_data, img_width, img_height):
        """
        Merges UI elements and OCR text to form a tree.
        1. Associates text with identifying bounding boxes.
        2. Infers hierarchy (parent-child based on containment).
        3. Returns a JSON-serializable dict tree.
        """
        
        # Combine elements and text into a unified node list
        nodes = []
        
        # Add shape elements
        for el in elements:
            nodes.append({
                "type": "container", # Default to container
                "box": el['box'],
                "children": [],
                "text": None
            })
            
        # Add text elements (and try to merge with containers if they overlap significantly)
        for ocr in ocr_data:
            nodes.append({
                "type": "text",
                "box": ocr['box'],
                "children": [],
                "text": ocr['text']
            })

        # Simple hierarchical sort: Larger contain smaller
        # First, sort by area descending (so big containers come first)
        nodes.sort(key=lambda n: n['box'][2] * n['box'][3], reverse=True)

        root = {
            "type": "root",
            "box": [0, 0, img_width, img_height],
            "children": []
        }

        # Iterative insertion into tree
        remaining_nodes = nodes.copy()
        
        # Basic O(N^2) insertion for now
        # We start with the root. For each node, we try to put it into the deepest possible child of root.
        
        def is_contained(inner, outer):
            ix, iy, iw, ih = inner['box']
            ox, oy, ow, oh = outer['box']
            return (ix >= ox) and (iy >= oy) and (ix + iw <= ox + ow) and (iy + ih <= oy + oh)

        def insert_node(parent, node):
            # Try to find a child of parent that contains this node
            for child in parent['children']:
                if is_contained(node, child):
                    insert_node(child, node)
                    return
            
            # If no child contains it, add it to this parent
            parent['children'].append(node)

        for node in nodes:
            # Skip nodes that are basically the whole image
            if node['box'][2] > img_width * 0.95 and node['box'][3] > img_height * 0.95:
                continue
            insert_node(root, node)

        return root
