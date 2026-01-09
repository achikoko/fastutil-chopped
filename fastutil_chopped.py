import os
import shutil
from typing import Callable, Optional

class Type:
    def __init__(self, idx: int, lc_name: str, lc_name2: str = None):
        self.idx = idx
        self.lc_name = lc_name
        self.lc_name2 = lc_name2

    @property
    def lc(self):
        return self.lc_name

    @property
    def lc2(self):
        return self.lc_name2 if self.lc_name2 is not None else self.lc_name

    @property
    def cap(self):
        return str(self.lc[0]).upper() + self.lc[1:]

    @property
    def cap2(self):
        return str(self.lc2[0]).upper() + self.lc2[1:]

    @property
    def index(self):
        return self.idx

boolean=Type(0, 'boolean')
byte=Type(1, 'byte')
short=Type(2, 'short')
intt=Type(3, 'int')
long=Type(4, 'long')
char=Type(5, 'char')
floatt=Type(6, 'float')
double=Type(7, 'double')
object=Type(8, 'object')
reference=Type(9, 'reference', 'object')

TYPES = [
    boolean, byte, short, intt, long, char, floatt, double, object, reference
]

class SourceFileTemplate:

    def __init__(self, pref: str, suf: str, *type_exclusions: Type):
        self.suf = suf
        self.pref = pref
        self.type_exclusions = type_exclusions

    def get_file_for_type(self, type: Type):
        for r in self.type_exclusions:
            if r == type:
                return None
        return SourceFile(type.lc2 + 's', self.pref + type.cap + self.suf, source_file_template=self, type1=type)


class DoubleSourceFileTemplate:

    def __init__(self, pref: str, inf: str, suf: str):
        self.suf = suf
        self.inf = inf
        self.pref = pref

        self.__all_except: Optional[list[tuple[Type, Type]]] = None
        self.__no_except: Optional[list[tuple[Type, Type]]] = None
        self.__only_same_type_except: Optional[list[Type]] = None
        self.__only_if_first_is: Optional[list[Type]] = None
        self.__only_if_first_is_not: Optional[list[Type]] = None
        self.__only_if_second_is_not: Optional[list[Type]] = None

    def get_file_for_types(self, type1: Type, type2: Type):
        constant_type1 = type1
        constant_type2 = type2

        if self.__all_except is not None:
            for t1, t2 in self.__all_except:
                if constant_type1 == t1 and constant_type2 == t2:
                    return None

        if self.__no_except is not None:
            for t1, t2 in self.__no_except:
                if constant_type1 == t1 and constant_type2 == t2:
                    break
            else:
                return None

        if self.__only_same_type_except is not None:
            if constant_type1 != constant_type2:
                return None
            for t in self.__only_same_type_except:
                if constant_type1 == t:
                    return None

        if self.__only_if_first_is is not None:
            for t in self.__only_if_first_is:
                if t != constant_type1:
                    return None

        if self.__only_if_first_is_not is not None:
            for t in self.__only_if_first_is_not:
                if t == constant_type1:
                    return None

        if self.__only_if_second_is_not is not None:
            for t in self.__only_if_second_is_not:
                if t == constant_type2:
                    return None

        return SourceFile(type1.lc2 + 's', self.pref + type1.cap + self.inf + type2.cap + self.suf, double_source_file_template=self, type1=type1, type2=type2)

    def only_same_type_except(self, *types: Type) -> 'DoubleSourceFileTemplate':
        self.__only_same_type_except = [*types]
        return self

    def all_except(self, *type_tuples: tuple[Type, Type]) -> 'DoubleSourceFileTemplate':
        self.__all_except = [*type_tuples]
        return self

    def no_except(self, *type_tuples: tuple[Type, Type]) -> 'DoubleSourceFileTemplate':
        self.__no_except = [*type_tuples]
        return self

    def only_if_first_is(self, *types: Type) -> 'DoubleSourceFileTemplate':
        self.__only_if_first_is = [*types]
        return self

    def only_if_first_is_not(self, *types: Type) -> 'DoubleSourceFileTemplate':
        self.__only_if_first_is_not = [*types]
        return self

    def only_if_second_is_not(self, *types: Type) -> 'DoubleSourceFileTemplate':
        self.__only_if_second_is_not = [*types]
        return self


class SourceFile:

    def __init__(
            self,
            folder: Optional[str],
            file_name: str,
            *,
            source_file_template: SourceFileTemplate = None,
            double_source_file_template: DoubleSourceFileTemplate = None,
            type1: Type = None,
            type2: Type = None
    ):
        self.folder = folder
        self.file_name = file_name

        self.source_file_template = source_file_template
        self.double_source_file_template = double_source_file_template

        self.used = False

        self.type1 = type1
        self.type2 = type2

    def get_file_name(self):
        return self.file_name + '.java'

    def __hash__(self):
        return hash(self.file_name + '.java')

    def __eq__(self, other):
        if isinstance(other, str):
            return (self.file_name + '.java') == other
        else:
            return super().__eq__(other)

    def __repr__(self):
        return self.file_name + '.java'

    def get_file_name_with_dir(self):
        return (self.folder + '/' if self.folder is not None else '/') + self.file_name + '.java'


type_source_file_defs: list[SourceFileTemplate] = [
    SourceFileTemplate('Abstract', 'BidirectionalIterator', reference),
    SourceFileTemplate('Abstract', 'BigList'),
    SourceFileTemplate('Abstract', 'BigListIterator', reference),
    SourceFileTemplate('Abstract', 'Collection'),
    SourceFileTemplate('Abstract', 'Comparator', boolean, object, reference),
    SourceFileTemplate('Abstract', 'Iterator', reference),
    SourceFileTemplate('Abstract', 'List'),
    SourceFileTemplate('Abstract', 'ListIterator', reference),
    SourceFileTemplate('Abstract', 'PriorityQueue', boolean, object, reference),
    SourceFileTemplate('Abstract', 'Set'),
    SourceFileTemplate('Abstract', 'SortedSet', boolean),
    SourceFileTemplate('Abstract', 'Spliterator', reference),
    SourceFileTemplate('Abstract', 'Stack', object, reference),
    SourceFileTemplate('', 'ArrayFIFOQueue', boolean, reference),
    SourceFileTemplate('', 'ArrayFrontCodedBigList', boolean, object, reference, floatt, double),
    SourceFileTemplate('', 'ArrayFrontCodedList', boolean, object, reference, floatt, double),
    SourceFileTemplate('', 'ArrayIndirectPriorityQueue', boolean, reference),
    SourceFileTemplate('', 'ArrayList'),
    SourceFileTemplate('', 'ArrayPriorityQueue', boolean, reference),
    SourceFileTemplate('', 'Arrays', reference),
    SourceFileTemplate('', 'ArraySet'),
    SourceFileTemplate('', 'AVLTreeSet', boolean, reference),
    SourceFileTemplate('', 'BidirectionalIterable', reference),
    SourceFileTemplate('', 'BidirectionalIterator', reference),
    SourceFileTemplate('', 'BigArrayBigList'),
    SourceFileTemplate('', 'BigArrays', reference),
    SourceFileTemplate('', 'BigList'),
    SourceFileTemplate('', 'BigListIterator', reference),
    SourceFileTemplate('', 'BigListIterators', reference),
    SourceFileTemplate('', 'BigLists'),
    SourceFileTemplate('', 'BigSpliterators', reference),
    SourceFileTemplate('', 'BinaryOperator', object, reference),
    SourceFileTemplate('', 'Collection'),
    SourceFileTemplate('', 'Collections'),
    SourceFileTemplate('', 'Comparator', object, reference),
    SourceFileTemplate('', 'Comparators', reference),
    SourceFileTemplate('', 'Consumer', object, reference),

    SourceFileTemplate('', 'Hash', object, reference),

    SourceFileTemplate('', 'HeapIndirectPriorityQueue', boolean, reference),
    SourceFileTemplate('', 'HeapPriorityQueue', boolean, reference),
    SourceFileTemplate('', 'Heaps', boolean, reference),
    SourceFileTemplate('', 'HeapSemiIndirectPriorityQueue', boolean, reference),

    SourceFileTemplate('', 'ImmutableList'),
    SourceFileTemplate('', 'IndirectHeaps', boolean, reference),
    SourceFileTemplate('', 'IndirectPriorityQueue', boolean, object, reference),

    SourceFileTemplate('', 'Iterable', reference),
    SourceFileTemplate('', 'Iterables', reference),
    SourceFileTemplate('', 'Iterator', reference),
    SourceFileTemplate('', 'Iterators', reference),

    SourceFileTemplate('', 'LinkedOpenCustomHashSet', boolean, reference),
    SourceFileTemplate('', 'LinkedOpenHashSet', boolean),

    SourceFileTemplate('', 'List'),
    SourceFileTemplate('', 'ListIterator', reference),
    SourceFileTemplate('', 'Lists'),

    SourceFileTemplate('', 'MappedBigList', boolean, object, reference),

    SourceFileTemplate('', 'OpenCustomHashSet', boolean, reference),
    SourceFileTemplate('', 'OpenHashBigSet', boolean, byte, short, char),
    SourceFileTemplate('', 'OpenHashSet'),

    SourceFileTemplate('', 'Predicate', object, reference),
    SourceFileTemplate('', 'PriorityQueue', boolean, object, reference),
    SourceFileTemplate('', 'PriorityQueues', boolean, object, reference),

    SourceFileTemplate('', 'RBTreeSet', boolean, reference),

    SourceFileTemplate('', 'SemiIndirectHeaps', boolean, reference),

    SourceFileTemplate('', 'Set'),
    SourceFileTemplate('', 'Sets'),
    SourceFileTemplate('', 'SortedSet', boolean),
    SourceFileTemplate('', 'SortedSets', boolean),
    SourceFileTemplate('', 'Spliterator', reference),
    SourceFileTemplate('', 'Spliterators', reference),
    SourceFileTemplate('', 'Stack', object, reference),
    SourceFileTemplate('', 'UnaryOperator', object, reference),
]


type_double_source_file_defs: list[DoubleSourceFileTemplate] = [
    DoubleSourceFileTemplate('Abstract', '2', 'Function'),
    DoubleSourceFileTemplate('Abstract', '2', 'Map').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('Abstract', '2', 'SortedMap').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'ArrayMap').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'AVLTreeMap').only_if_first_is_not(boolean, reference),
    DoubleSourceFileTemplate('', '2', 'Function'),
    DoubleSourceFileTemplate('', '2', 'Functions').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'LinkedOpenHashMap').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'LinkedOpenCustomHashMap').only_if_first_is(object),
    DoubleSourceFileTemplate('', '2', 'Map').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'Maps').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'OpenCustomHashMap').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'OpenHashMap').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'RBTreeMap').only_if_first_is_not(boolean, reference),
    DoubleSourceFileTemplate('', '2', 'SortedMap').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '2', 'SortedMaps').only_if_first_is_not(boolean),
    DoubleSourceFileTemplate('', '', 'BiConsumer').only_if_first_is_not(reference).only_if_second_is_not(reference).all_except((object, object)),
    # DoubleSourceFileTemplate('', '', 'BiConsumer').no_except((reference, reference)),

    DoubleSourceFileTemplate('', '', 'ImmutablePair'),
    DoubleSourceFileTemplate('', '', 'MutablePair'),
    DoubleSourceFileTemplate('', '', 'Pair').all_except((object, object)),
    DoubleSourceFileTemplate('', '', 'ImmutableSortedPair').only_same_type_except(boolean, reference),
    DoubleSourceFileTemplate('', '', 'SortedPair').only_same_type_except(boolean, reference, object)
]

AbstractIndirectPriorityQueue = SourceFile(None, 'AbstractIndirectPriorityQueue')
AbstractPriorityQueue = SourceFile(None, 'AbstractPriorityQueue')
AbstractStack = SourceFile(None, 'AbstractStack')
Arrays = SourceFile(None, 'Arrays')
BidirectionalIterator = SourceFile(None, 'BidirectionalIterator')
BigArrays = SourceFile(None, 'BigArrays')
BigList = SourceFile(None, 'BigList')
BigListIterator = SourceFile(None, 'BigListIterator')
BigSwapper = SourceFile(None, 'BigSwapper')
Function = SourceFile(None, 'Function')
Hash = SourceFile(None, 'Hash')
HashCommon = SourceFile(None, 'HashCommon')
IndirectPriorityQueue = SourceFile(None, 'IndirectPriorityQueue')
IndirectPriorityQueues = SourceFile(None, 'IndirectPriorityQueues')
Pair = SourceFile(None, 'Pair')
PriorityQueue = SourceFile(None, 'PriorityQueue')
PriorityQueues = SourceFile(None, 'PriorityQueues')
SafeMath = SourceFile(None, 'SafeMath')
Size64 = SourceFile(None, 'Size64')
SortedPair = SourceFile(None, 'SortedPair')
Stack = SourceFile(None, 'Stack')
Swapper = SourceFile(None, 'Swapper')

all_common_files: list[SourceFile] = [
    AbstractIndirectPriorityQueue,
    AbstractPriorityQueue,
    AbstractStack,
    Arrays,
    BidirectionalIterator,
    BigArrays,
    BigList,
    BigListIterator,
    BigSwapper,
    Function,
    Hash,
    HashCommon,
    IndirectPriorityQueue,
    IndirectPriorityQueues,
    Pair,
    PriorityQueue,
    PriorityQueues,
    SafeMath,
    Size64,
    SortedPair,
    Stack,
    Swapper,
]

BinIO = SourceFile('io', 'BinIO')
FastBufferedInputStream = SourceFile('io', 'FastBufferedInputStream')
FastBufferedOutputStream = SourceFile('io', 'FastBufferedOutputStream')
FastByteArrayInputStream = SourceFile('io', 'FastByteArrayInputStream')
FastByteArrayOutputStream = SourceFile('io', 'FastByteArrayOutputStream')
FastMultiByteArrayInputStream = SourceFile('io', 'FastMultiByteArrayInputStream')
InspectableFileCachedInputStream = SourceFile('io', 'InspectableFileCachedInputStream')
MeasurableInputStream = SourceFile('io', 'MeasurableInputStream')
MeasurableOutputStream = SourceFile('io', 'MeasurableOutputStream')
MeasurableStream = SourceFile('io', 'MeasurableStream')
RepositionableStream = SourceFile('io', 'RepositionableStream')
TextIO = SourceFile('io', 'TextIO')

all_io_files: list[SourceFile] = [
    BinIO,
    FastBufferedInputStream,
    FastBufferedOutputStream,
    FastByteArrayInputStream,
    FastByteArrayOutputStream,
    FastMultiByteArrayInputStream,
    InspectableFileCachedInputStream,
    MeasurableInputStream,
    MeasurableOutputStream,
    MeasurableStream,
    RepositionableStream,
    TextIO,
]

def check_all_files_written(all_projected_files: list[SourceFile]):
    written = 0
    remaining = 0
    for s in all_projected_files:
        if s.used:
            written += 1
        else:
            print(f'{remaining}    {s.file_name}')
            remaining += 1
    print(f'All files: {len(all_projected_files)}')
    print(f'Written files: {written}')


def check_all_files_exist():

    maven_source_src = ORIGINAL_FASTUTIL_FOLDER + '/src' + BASE_PACKAGE_FOLDER

    all_original_files = set()

    for f in os.listdir(maven_source_src):
        if f.endswith('.java') and not f.startswith('package-info'):
            all_original_files.add(f)

    for f in os.listdir(maven_source_src + '/io'):
        if f.endswith('.java') and not f.startswith('package-info'):
            all_original_files.add(f)

    for type_name in TYPES:
        for f in os.listdir(maven_source_src + '/' + type_name.lc2 + 's'):
            if f.endswith('.java') and not f.startswith('package-info'):
                all_original_files.add(f)

    print(f'Number of java files in original project: {len(all_original_files)}')

    all_projected_files: list[SourceFile] = [
        *all_common_files,
        *all_io_files
    ]
    all_projected_files_names = set()

    for common_file in all_common_files:
        all_projected_files_names.add(common_file.get_file_name())

    for io_file in all_io_files:
        all_projected_files_names.add(io_file.get_file_name())

    for type_index in TYPES:
        for source_def in type_source_file_defs:
            f = source_def.get_file_for_type(type_index)
            if f is not None:
                all_projected_files.append(f)
                all_projected_files_names.add(f.get_file_name())

    for type_index_1 in TYPES:
        for type_index_2 in TYPES:
            for double_source_def in type_double_source_file_defs:
                f = double_source_def.get_file_for_types(type_index_1, type_index_2)
                if f is not None:
                    all_projected_files.append(f)
                    all_projected_files_names.add(f)

    print(f'Number of java files projected: {len(all_projected_files)}')

    i_original = 0
    for original in all_original_files:
        if original not in all_projected_files:
            if i_original == 0:
                print(f'Files that exist in original but not in projected: ')
            print(f'{i_original}    {original}')
            i_original += 1


    i_projected = 0
    for projected in all_projected_files:
        if projected.get_file_name() not in all_original_files:
            if i_projected == 0:
                print(f'Files that exist in projected but not in original: ')
            print(f'{i_projected}    {projected}')
            i_projected += 1

    if i_original != 0 or i_projected != 0:
        raise Exception('Files got outdated, aborting.')

    return all_projected_files

Filter = Callable[[SourceFile], bool]
Actuator = Callable[[SourceFile, str], None]

class Package:

    def __init__(self, prefix: str, type1: Type = None, type2: Type = None):

        self.prefix = prefix
        self.type1 = type1
        self.type2 = type2

        if type1 is None and type2 is None:
            self.name = prefix
        elif type2 is None:
            self.name = prefix + "-" + type1.lc_name
        else:
            self.name = prefix + "-" + type1.lc_name + "-" + type2.lc_name

        self.filters: list[Filter] = []
        self.dependencies: set['Package'] = set()
        self.actuators: list[Actuator] = []

    def add_filter(self, filter: Filter) -> 'Package':
        if filter is not None:
            self.filters.append(filter)
        return self

    def add_dependency(self, dep: 'Package') -> 'Package':
        if dep is not None:
            self.dependencies.add(dep)
        return self

    def add_actuator(self, actuator: Actuator) -> 'Package':
        if actuator is not None:
            self.actuators.append(actuator)
        return self

    def includes(self, projected_file: SourceFile):
        for filter in self.filters:
            if filter(projected_file):
                return True
        return False

    def actuate(self, recently_copied_file_file: SourceFile, base_path: str):
        for actuator in self.actuators:
            actuator(recently_copied_file_file, base_path)

    def include_all_of(self, other: 'Package') -> 'Package':
        self.filters.extend(other.filters)
        self.dependencies.update(other.dependencies)
        self.actuators.extend(other.actuators)

        if self.type1 is None and other.type1 is None:
            self.name = self.prefix
        elif other.type1 is None:
            self.name = self.prefix + "-" + self.type1.lc_name
        else:
            self.name = self.prefix + "-" + self.type1.lc_name + "-" + other.type1.lc_name

        return self


def select_by_folder(folder_name: Optional[str]):
    def selector(source: SourceFile):
        return source.folder == folder_name
    return selector

def select_by_name_startswith(name_starts: Optional[str]):
    def selector(source: SourceFile):
        return source.file_name.startswith(name_starts)
    return selector

def select_by_name_endswith(name_starts: Optional[str]):
    def selector(source: SourceFile):
        return source.file_name.endswith(name_starts)
    return selector

def select_by_suffix_endswith(suffix_end: Optional[str]):
    def selector(source: SourceFile):
        if source.source_file_template is not None:
            return source.source_file_template.suf.endswith(suffix_end)
        if source.double_source_file_template is not None:
            return source.double_source_file_template.suf.endswith(suffix_end)
        return source.file_name.endswith(suffix_end)
    return selector

def select_by_suffix_equals(suffix_equals: Optional[str]):
    def selector(source: SourceFile):
        if source.source_file_template is not None:
            return source.source_file_template.suf == suffix_equals
        if source.double_source_file_template is not None:
            return source.double_source_file_template.suf == suffix_equals
        return source.file_name == suffix_equals
    return selector

def select_by_prefix_startswith(prefix_start: Optional[str]):
    def selector(source: SourceFile):
        if source.source_file_template is not None:
            return source.source_file_template.pref.startswith(prefix_start)
        if source.double_source_file_template is not None:
            return source.double_source_file_template.pref.startswith(prefix_start)
        return source.file_name.startswith(prefix_start)
    return selector

def select_by_single_type(type: Optional[Type]):
    def selector(source: SourceFile):
        if type is None:
            return source.source_file_template is None and source.double_source_file_template is None
        if source.source_file_template is not None:
            return source.type1 == type
        return False
    return selector

def select_by_double_type1(type1: Type):
    def selector(source: SourceFile):
        if source.double_source_file_template is not None:
            return source.type1 == type1
        return False
    return selector

def select_by_double_type2(type2: Type):
    def selector(source: SourceFile):
        if source.double_source_file_template is not None:
            return source.type2 == type2
        return False
    return selector

def select_anded(*selectors_to_and: Filter) -> Filter:
    def selector(source: SourceFile) -> boolean:
        for selector_to_and in selectors_to_and:
            if not selector_to_and(source):
                return False
        return True
    return selector

def select_ord(*selectors_to_and: Filter) -> Filter:
    def selector(source: SourceFile) -> boolean:
        for selector_to_and in selectors_to_and:
            if selector_to_and(source):
                return True
        return False
    return selector

def select_not(selector_to_negate: Filter) -> Filter:
    def selector(source: SourceFile) -> boolean:
        return not selector_to_negate(source)
    return selector

def actuator_replace_string_on_file(file_name: str, search: str, replace: str):
    def actuator(source: SourceFile, base_path: str):
        if source.file_name == file_name:
            with open(base_path + "/" + source.get_file_name_with_dir(), 'r') as file:
                content = file.read()
            content = content.replace(search, replace)
            with open(base_path + "/" + source.get_file_name_with_dir(), 'w') as file:
                file.write(content)

    return actuator


def copy_bom_pom(packages: list[Package]):

    maven_project_folder = PREFIX + '/' + MAVEN_PARENT_ARTIFACT_ID + '-bom'

    with open('pom-bom.template.xml', 'r') as file:
        pom_global = file.read()

    pom_global = pom_global.replace('@GROUP_ID@', MAVEN_GROUP_ID)
    pom_global = pom_global.replace('@PARENT_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID)
    pom_global = pom_global.replace('@VERSION@', MAVEN_VERSION)

    pom_global = pom_global.replace('@BOM_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID + '-bom')

    with open('pom-module.template.xml', 'r') as file:
        module_template = file.read()

    modules = ''
    for package in packages:
        modules += module_template.replace('@MODULE@', '../' + MAVEN_PARENT_ARTIFACT_ID + '-' + package.name)
    pom_global = pom_global.replace('@MODULES@', modules)


    with open('pom-dependency.template.xml', 'r') as file:
        dependency_template = file.read()

    dependencies = ''
    for package in packages:
        dependencies += dependency_template.replace('@DEPENDENCY_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID + '-' + package.name)

    pom_global = pom_global.replace('@DEPENDENCIES@', dependencies)

    os.makedirs(maven_project_folder, exist_ok=True)
    with open(maven_project_folder + '/pom.xml', 'w') as file:
        file.write(pom_global)


def copy_parent_pom():

    maven_project_folder = PREFIX

    with open('pom-parent.template.xml', 'r') as file:
        pom_parent = file.read()

    pom_parent = pom_parent.replace('@GROUP_ID@', MAVEN_GROUP_ID)
    pom_parent = pom_parent.replace('@PARENT_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID)
    pom_parent = pom_parent.replace('@VERSION@', MAVEN_VERSION)
    pom_parent = pom_parent.replace('@BOM_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID + '-bom')

    with open('pom-extra.template.xml', 'r') as file:
        extra_template = file.read()

    pom_parent = pom_parent.replace('@EXTRA@', extra_template)

    with open(maven_project_folder + '/pom.xml', 'w') as file:
        file.write(pom_parent)


def copy_local_type_pom(package: Package):

    maven_project_folder = PREFIX + '/' + MAVEN_PARENT_ARTIFACT_ID + '-' + package.name

    with open('pom-local.template.xml', 'r') as file:
        pom_local = file.read()

    pom_local = pom_local.replace('@GROUP_ID@', MAVEN_GROUP_ID)
    pom_local = pom_local.replace('@BOM_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID + '-bom')
    pom_local = pom_local.replace('@VERSION@', MAVEN_VERSION)
    pom_local = pom_local.replace('@BOM_RELATIVE_PATH@', '../' + MAVEN_PARENT_ARTIFACT_ID + '-bom')
    pom_local = pom_local.replace('@LOCAL_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID + '-' + package.name)

    if len(package.dependencies) > 0:

        with open('pom-dependency.template.xml', 'r') as file:
            dependency_template = file.read()

        dependencies = ''
        for dep in package.dependencies:
            dependencies += dependency_template.replace('@DEPENDENCY_ARTIFACT_ID@', MAVEN_PARENT_ARTIFACT_ID + '-' + dep.name)

        pom_local = pom_local.replace('@DEPENDENCIES@', dependencies)
    else:
        pom_local = pom_local.replace('@DEPENDENCIES@', '')

    with open(maven_project_folder + '/pom.xml', 'w') as file:
        file.write(pom_local)


def create_package(package: Package, all_projected_files: list[SourceFile], fail_if_used = False):
    maven_project_folder = PREFIX + '/' + MAVEN_PARENT_ARTIFACT_ID + '-' + package.name
    os.makedirs(maven_project_folder, exist_ok=True)

    maven_source_src = ORIGINAL_FASTUTIL_FOLDER + '/src' + BASE_PACKAGE_FOLDER
    maven_source_dst = maven_project_folder + '/src/main/java' + BASE_PACKAGE_FOLDER
    os.makedirs(maven_source_dst, exist_ok=True)

    created_folders: set[str] = set()

    for projected_file in all_projected_files:
        used = projected_file.used
        if not used:
            includes = package.includes(projected_file)
            if includes:
                projected_file.used = True

                if projected_file.folder is not None and projected_file.folder not in created_folders:
                    os.makedirs(maven_source_dst + '/' + projected_file.folder, exist_ok=True)

                shutil.copyfile(
                    maven_source_src + '/' + projected_file.get_file_name_with_dir(),
                    maven_source_dst + '/' + projected_file.get_file_name_with_dir()
                )

                package.actuate(projected_file, maven_source_dst)

        elif fail_if_used:
            includes = package.includes(projected_file)
            if includes:
                raise Exception(f'File {projected_file.get_file_name_with_dir()} referenced multiple times.')

    copy_local_type_pom(package)


def main():
    all_projected_files = check_all_files_exist()

    packages = []

    module_hash = (
        Package('hash')
        .add_filter(select_by_name_endswith('Hash'))
        .add_filter(select_by_name_endswith('HashCommon'))
    )
    packages.append(module_hash)

    module_pair = (
        Package('pair')
        .add_filter(select_by_suffix_endswith('Pair'))
        .add_dependency(module_hash)
    )
    packages.append(module_pair)

    module_functions = (
        Package('functions')
        .add_filter(select_by_name_startswith('SafeMath'))
        .add_filter(select_by_suffix_endswith('Functions'))
        .add_filter(select_by_suffix_endswith('Function'))
        .add_filter(select_by_suffix_endswith('Consumer')) # and 'BiConsumer'
        .add_filter(select_by_suffix_endswith('Consumers'))
        .add_filter(select_by_suffix_endswith('Predicate'))
        .add_filter(select_by_suffix_endswith('Predicates'))
        .add_filter(select_by_suffix_endswith('UnaryOperator'))
        .add_filter(select_by_suffix_endswith('BinaryOperator'))
    )
    packages.append(module_functions)

    module_comparators = (
        Package('comparators')
        .add_filter(select_by_suffix_endswith('Comparators'))
        .add_filter(select_by_suffix_endswith('Comparator'))
        .add_dependency(module_functions)
    )
    packages.append(module_comparators)

    module_arrays = (
        Package('arrays')
        .add_filter(select_by_name_startswith('Swapper'))
        .add_filter(select_anded(select_by_suffix_endswith('Arrays'), select_not(select_by_suffix_endswith('BigArrays'))))
        .add_dependency(module_hash)
        .add_dependency(module_comparators)
    )
    packages.append(module_arrays)

    module_bigarrays = (
        Package('bigarrays')
        .add_filter(select_by_name_startswith('BigSwapper'))
        .add_filter(select_by_suffix_endswith('BigArrays'))
        .add_actuator(actuator_replace_string_on_file('BigArrays', 'import it.unimi.dsi.fastutil.ints.IntBigArrayBigList;', '// import it.unimi.dsi.fastutil.ints.IntBigArrayBigList;'))
        .add_actuator(actuator_replace_string_on_file('BigArrays', '{@link IntBigArrayBigList}', '{@link it.unimi.dsi.fastutil.ints.IntBigArrayBigList}'))
        .add_dependency(module_hash)
        .add_dependency(module_comparators)
        .add_dependency(module_arrays)
    )
    packages.append(module_bigarrays)

    module_collections = (
        Package('collections')
        .add_filter(select_by_name_startswith('Size64'))
        .add_filter(select_by_suffix_endswith('Iterable'))
        .add_filter(select_by_suffix_endswith('Iterables'))
        .add_filter(select_by_suffix_endswith('Iterator'))
        .add_filter(select_by_suffix_endswith('Iterators'))
        .add_filter(select_by_suffix_endswith('Spliterator'))
        .add_filter(select_by_suffix_endswith('Spliterators'))
        .add_filter(select_by_suffix_endswith('Collection'))
        .add_filter(select_by_suffix_endswith('Collections'))
        .add_filter(select_by_suffix_endswith('ArrayFrontCodedList'))
        .add_filter(select_by_suffix_endswith('List'))
        .add_filter(select_by_suffix_endswith('ImmutableList'))
        .add_filter(select_by_suffix_endswith('ArrayList'))
        .add_filter(select_by_suffix_endswith('Lists'))
        .add_filter(select_by_suffix_endswith('Stack'))
        .add_dependency(module_bigarrays)
        .add_dependency(module_functions)
    )
    packages.append(module_collections)

    def create_biglists(type: Type):
        return (
            Package('biglists', type)
                .add_filter(select_anded(
                    select_by_single_type(type),
                    select_by_suffix_endswith('BigLists'),
                ))
                .add_filter(select_anded(
                    select_by_single_type(type),
                    select_by_suffix_endswith('BigList'),
                ))
                .add_filter(select_anded(
                    select_by_single_type(type),
                    select_by_suffix_endswith('MappedBigList'),
                ))
                .add_filter(select_anded(
                    select_by_single_type(type),
                    select_by_suffix_endswith('BigListIterator'),
                ))
                .add_dependency(module_comparators)
                .add_dependency(module_collections)
                .add_dependency(module_bigarrays)
                )

    biglists = []

    for type in TYPES:
        biglists.append(
            create_biglists(type)
        )

    packages.extend(biglists)

    sets = []

    for type in TYPES:
        sets.append(
            Package('sets', type)
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_prefix_startswith('Abstract'),
                select_by_suffix_endswith('Set'),
            ))
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_suffix_endswith('Set'),
            ))
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_suffix_endswith('Sets'),
            ))
            .add_dependency(module_collections)
        )

    packages.extend(sets)

    maps = []

    for type1 in TYPES[1:]:
        for type2 in TYPES:
            maps.append(
                Package('maps', type1, type2)
                .add_filter(select_anded(
                    select_by_double_type1(type1),
                    select_by_double_type2(type2),
                    select_by_prefix_startswith('Abstract'),
                    select_by_suffix_endswith('Map'),
                ))
                .add_filter(select_anded(
                    select_by_double_type1(type1),
                    select_by_double_type2(type2),
                    select_by_suffix_endswith('Map'),
                ))
                .add_filter(select_anded(
                    select_by_double_type1(type1),
                    select_by_double_type2(type2),
                    select_by_suffix_endswith('Maps'),
                ))
                .add_dependency(module_pair)
                .add_dependency(module_collections) # Maps are the only dependent of BiConsumers, but they are in functions <- collections <- maps
                .add_dependency(sets[object.idx]) # Everybody wants objects
                .add_dependency(sets[type1.idx] if type1 != object else None) # Add counterpart set
                .add_dependency(sets[type2.idx] if type2 != object else None) # Add counterpart set
            )

    packages.extend(maps)

    module_io = (
        Package('io')
        .add_filter(select_by_suffix_endswith('InputStream'))
        .add_filter(select_by_suffix_endswith('OutputStream'))
        .add_filter(select_by_suffix_equals('MeasurableStream'))
        .add_filter(select_by_suffix_equals('RepositionableStream'))
        .add_filter(select_by_suffix_equals('BinIO'))
        .add_filter(select_by_suffix_equals('TextIO'))
        .add_dependency(module_arrays)
        .add_dependency(module_bigarrays)
        .add_dependency(module_collections)
    )
    packages.append(module_io)

    module_priorityqueues = (
        Package('priorityqueues')
        .add_filter(select_anded(
            select_by_single_type(None),
            select_by_prefix_startswith('Abstract'),
            select_by_suffix_endswith('PriorityQueue'),
        ))
        .add_filter(select_anded(
            select_by_single_type(None),
            select_by_suffix_equals('PriorityQueue'),
        ))
        .add_filter(select_by_name_startswith('PriorityQueues'))
        .add_filter(select_by_name_startswith('IndirectPriorityQueue'))
        .add_filter(select_by_name_startswith('IndirectPriorityQueues'))
        .add_dependency(module_collections)
    )
    packages.append(module_priorityqueues)

    priorityqueues = []

    for type in TYPES[1:-1]: # no boolean nor reference
        priorityqueues.append(
            Package('priorityqueues', type)
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_prefix_startswith('Abstract'),
                select_by_suffix_endswith('PriorityQueue'),
            ))
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_suffix_endswith('ArrayFIFOQueue'),
            ))
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_suffix_endswith('PriorityQueue'),
            ))
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_suffix_endswith('PriorityQueues'),
            ))
            .add_filter(select_anded(
                select_by_single_type(type),
                select_by_suffix_endswith('Heaps'),
            ))
            .add_dependency(module_pair)
            .add_dependency(module_collections)
            .add_dependency(module_arrays)
            .add_dependency(module_priorityqueues)
        )

    packages.extend(priorityqueues)

    for package in packages:
        create_package(package, all_projected_files, False)

    copy_bom_pom(packages)
    copy_parent_pom()

    check_all_files_written(all_projected_files)


if __name__ == '__main__':

    global PREFIX, BASE_PACKAGE_FOLDER, ORIGINAL_FASTUTIL_FOLDER, MAVEN_GROUP_ID, MAVEN_PARENT_ARTIFACT_ID, MAVEN_VERSION

    PREFIX = 'maven-project'
    BASE_PACKAGE_FOLDER = '/it/unimi/dsi/fastutil'

    ORIGINAL_FASTUTIL_FOLDER = 'fastutil'

    # MAVEN_GROUP_ID = 'io.github.achiikun.fastutil'
    MAVEN_PARENT_ARTIFACT_ID = 'fastutil'
    MAVEN_VERSION = '8.5.18'

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--maven-group-id", type=str, help="Maven group ID. For example: it.unimi.dsi")
    args = parser.parse_args()

    MAVEN_GROUP_ID = args.maven_group_id

    main()
