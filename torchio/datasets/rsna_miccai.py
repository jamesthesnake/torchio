import csv
from typing import List
from pathlib import Path

from ..typing import TypePath
from .. import SubjectsDataset, Subject, ScalarImage


class RSNAMICCAI(SubjectsDataset):
    """RSNA-MICCAI Brain Tumor Radiogenomic Classification challenge dataset.

    This is a helper class for the dataset used in the
    `RSNA-MICCAI Brain Tumor Radiogenomic Classification challenge`_ hosted on
    `kaggle <https://www.kaggle.com/>`_. The dataset must be downloaded before
    instantiating this class (as oposed to, e.g., :class:`torchio.datasets.IXI`).

    If you reference or use the dataset in any form, include the following
    citation:

    U.Baid, et al., "The RSNA-ASNR-MICCAI BraTS 2021 Benchmark on Brain Tumor
    Segmentation and Radiogenomic Classification", arXiv:2107.02314, 2021.

    .. _RSNA-MICCAI Brain Tumor Radiogenomic Classification challenge: https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification
    """
    id_key = 'BraTS21ID'
    label_key = 'MGMT_value'
    modalities = 'T1w', 'T1wCE', 'T2w', 'FLAIR'

    def __init__(self, root_dir: TypePath, train: bool = True, **kwargs):
        self.root_dir = Path(root_dir).expanduser().resolve()
        subjects = self._get_subjects(self.root_dir, train)
        super().__init__(subjects, **kwargs)
        self.train = train

    def _get_subjects(self, root_dir: Path, train: bool) -> List[Subject]:
        subjects = []
        if train:
            csv_path = root_dir / 'train_labels.csv'
            with open(csv_path) as csvfile:
                reader = csv.DictReader(csvfile)
                labels_dict = {
                    row[self.id_key]: int(row[self.label_key])
                    for row in reader
                }
            subjects_dir = root_dir / 'train'
        else:
            subjects_dir = root_dir / 'test'

        for subject_dir in sorted(subjects_dir.iterdir()):
            subject_id = subject_dir.name
            try:
                int(subject_id)
            except ValueError:
                continue
            images_dict = {self.id_key: subject_dir.name}
            if train:
                images_dict[self.label_key] = labels_dict[subject_id]
            for modality in self.modalities:
                image_dir = subject_dir / modality
                filepaths = list(image_dir.iterdir())
                num_files = len(filepaths)
                path = filepaths[0] if num_files == 1 else image_dir
                images_dict[modality] = ScalarImage(path)
            subject = Subject(images_dict)
            subjects.append(subject)
        return subjects
