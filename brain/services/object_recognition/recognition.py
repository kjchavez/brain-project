import os, sys
import re
import time
import numpy as np
import tensorflow as tf
import argparse
import logging


class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self, label_lookup_path, uid_lookup_path):
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.

    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.

    Returns:
      dict from integer node ID to human-readable string.
    """
    if not os.path.isfile(uid_lookup_path):
      logging.fatal('File does not exist %s', uid_lookup_path)
    if not os.path.isfile(label_lookup_path):
      logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    with open(uid_lookup_path) as fp:
        proto_as_ascii_lines = fp.readlines()

    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    with open(label_lookup_path) as fp:
        proto_as_ascii = fp.readlines()

    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]


def create_graph(filename):
  """"Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.
  with open(filename, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')


class ObjectRecognizer(object):
    def __init__(self, graph_def_file, label_lookup_path, uid_lookup_path):
        create_graph(graph_def_file)
        self.node_lookup = NodeLookup(label_lookup_path, uid_lookup_path)

    def recognize(self, image_data, num_top_predictions=5):
      with tf.Session() as sess:
        # Some useful tensors:
        # 'softmax:0': A tensor containing the normalized prediction across
        #   1000 labels.
        # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
        #   float description of the image.
        # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
        #   encoding of the image.
        # Runs the softmax tensor by feeding the image_data as input to the graph.
        tic = time.time()
        softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions = np.squeeze(predictions)

        top_k = predictions.argsort()[-num_top_predictions:][::-1]
        human_predictions = []
        for node_id in top_k:
          human_string = self.node_lookup.id_to_string(node_id)
          score = predictions[node_id]
          human_predictions.append((human_string, score))

        toc = time.time()
        logging.debug("Object recogntion compute time: %0.2f ms",
                      (toc - tic)*1000)

        return human_predictions

def load_image(image):
    if not os.path.isfile(image):
      print 'File does not exist %s' % image
      sys.exit(1)

    with open(image, 'rb') as fp:
        image_data = fp.read()

    return image_data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", '-g', default='classify_image_graph_def.pb')
    parser.add_argument("--labels", '-l', default="imagenet_2012_challenge_label_map_proto.pbtxt")
    parser.add_argument("--uids", '-u', default="imagenet_synset_to_human_label_map.txt")
    parser.add_argument("--top_predictions", '-k', type=int, default=5)
    parser.add_argument("--image", '-i', default=None)

    return parser.parse_args()

def main():
    args = parse_args()

    model = ObjectRecognizer(args.graph, args.labels, args.uids)
    image_data = load_image(args.image)
    predictions = model.recognize(image_data, num_top_predictions=args.top_predictions)
    for human_string, score in predictions:
        print('%s (score = %.5f)' % (human_string, score))


if __name__ == "__main__":
    main()
