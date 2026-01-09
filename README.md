# Fastutil chopped

Vigna's [fastutil](https://github.com/vigna/fastutil) is a great library, very performant, very useful, but the **jar dependency** takes more that **22Mb** compressed.

The target of this project is to build the original fastutil project (linked as a submodule), and copy carefully all the _.java_ files into a multimodule **maven** project in order to reduce future dependent projects' size (as they will be able to import only the submodules they need).

Yes, this is a **python** project. I am adding this tool as an additional dependency besides java, maven, make, ant and cc because I prefer _python_ way longer than _shell_ scripting as a scripting language.

## Steps to Generate maven project

### Step 0
Assure you cloned the repository recursively and `fastutil` contains the raw fastutil project.

### Step 1 - Make original fastutil

Go into fastutil with `cd fastutil` and follow the instructions into the [fastutil/README.md](https://github.com/vigna/fastutil/blob/master/README.md) to generate all sources. It will require to execute `make sources` to generate them into the `src/` folder.

### Step 2 - Configure

- `cd ..` to get back to repo root.
- Modify the file `pom-extra.template.xml` to fill your needs, this file will be inserted inside the parent pom and lets you add deployment repositories and/or packaging repositories. Basically fill the `<build>` tag of the root pom.

### Step 3 - Execute the chopping

Execute

```
python fastutil_chopped.py --maven-group-id MAVEN_GROUP_ID
```

replacing `MAVEN_GROUP_ID` by your group id to generate the project inside the `maven-project` folder.

The script has a harcoded reference to all the files in the original project, then it is checking that all files in the original project are included and no one has been leftover or removed. This fact makes the project compatible only with the version that is currently submoduled, and future updates may break this code and, thus, need to be updated as well.

### Step 4 - Install/Deploy...

The chopped version of fastutil contains **127** submodules!! Basically every kind of biglist, set, map and priority queue has its own module. Arrays and Lists are compacted into a single module due to their complex interdependencies.

To install the project:

- `cd maven-project` to get into the maven project.
- `maven install` will copy all jars into your local maven repository.

## Future

I guess this repo has to be maintained when a new version of [fastutil](https://github.com/vigna/fastutil) is released.

There are near zero comments on the python file. I guess some hours have to be invested here?

## Licence

According to fastutil's Apache licence, this project only links the original project, and it is not considered "Derivative Work" but the original author is already mentioned. This project has an [MIT](LICENSE) permissive licence. No warranty is granted.
