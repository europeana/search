from urllib.parse import urldefrag, urlparse
import os
import zipfile

supported_langs = ["de", "el", "en", "es", "et", "fi", "fr", "hr", "it", "la", "lv", "nl", "pl", "ru", "sr",
                   "sv", "uk", "ar", "bg", "ca", "cz", "da", "eu", "fa", "ga", "gl", "hi", "hu", "hy", "id",
                   "no", "pt", "ro", "ja", "th", "tr", "ws", "und"]

def _validate_value(attr, value):
    """
    validate value before indexing

    :param value:
    :return:
    """
    if "[OCR confidence]" in str(value):
        return False

    if "proxy_dc_language" == str(attr) and str(value) not in supported_langs:
        return False

    return True


def ns_prefix_uri(uriref_str, namespace_dict):
    if '#' in uriref_str:
        url, frag = urldefrag(uriref_str)
        url = url + "#"
    else:
        url_list = uriref_str.rsplit('/', 1)
        url = url_list[0] + "/"
        frag = url_list[1]

    return "%s:%s"%(namespace_dict[url], frag)


def add_attr_value_multi(obj, attr, value):
    if not _validate_value(attr, value):
        return

    if hasattr(obj, attr):
        current_value = getattr(obj, attr, [])
        if str(value) not in current_value:
            current_value.append(str(value))

        # reduce duplications
        current_value = list(set(current_value))
        setattr(obj, attr, current_value)
    else:
        setattr(obj, attr, [str(value)])


def add_attr_value_single(obj, attr, value):
    setattr(obj, attr, value)


def load_resource_types(g, namespaces_dict, predicates):
    resource_type_dict = {}
    for pred in predicates:
        abbv_pred = ns_prefix_uri(pred, namespaces_dict)
        subject_object_tuples = g.subject_objects(pred)
        if "rdf:type" == abbv_pred:
            for obj_tuple in subject_object_tuples:
                resource_type_dict[obj_tuple[0]] = obj_tuple[1]
    return resource_type_dict


def load_files_path_from_dir(data_dir, file_suffix=".zip"):
    all_files = []
    for file in os.listdir(data_dir):
        if file.endswith(file_suffix):
            # skip entire issue alto zip file
            if file[0].isdigit():
                all_files.append(os.path.join(data_dir, file))
    return all_files


def extract_file_name(file_path, extension=".xml"):
    file_name = os.path.basename(os.path.normpath(file_path))
    return file_name.replace(extension, "")


def load_all_files_from_zip_file(zip_file_path):
    """
    extract all the file content from a zip file

    :param zip_file_path:
    :return: generator of every file raw content and file name
    """

    print("loading files from [%s] ... " % zip_file_path)
    zipped_files = zipfile.ZipFile(zip_file_path)
    all_files = zipped_files.filelist
    total_files_size = len(all_files)
    print("total file size: ", total_files_size)
    for f in zipped_files.namelist():
        file_name = extract_file_name(f)
        if not f.endswith("/"):
            xml_content = zipped_files.read(f)
            yield xml_content.decode(encoding='utf-8'), file_name, total_files_size


