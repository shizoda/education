# 医用画像処理の基礎知識

コンピュータによる画像処理や機械学習の応用例として、医用画像処理 (medical image processing) があります。

実習を試す上での最低限の基礎知識としてお読みください。なお初学者向けの簡潔な説明のため、厳密には実態と異なる箇所もある点にご留意ください。

## 医用画像

医用画像とは、人体の内部を可視化するために使用される画像です。これには、X線、CT（コンピュータ断層撮影）、MRI（磁気共鳴画像）、超音波などが含まれます。これらの画像は、疾患の診断、治療計画の策定、外科手術のガイドなど、医療のさまざまな場面で不可欠な役割を果たします。例えば、X線は骨折や肺の異常を検出するのに役立ち、MRIは軟部組織の詳細な画像を提供します。各モダリティは異なる種類の情報を提供し、特定の医療ニーズに最適化されています。

### CT 画像

Computed Tomography (CT, コンピュータ断層撮影) は、X線を用いて身体の内部を描出するための撮像技術です。患者を囲むように回転するX線管と検出器によって、体内の異なる角度から多数の画像を撮影し、これらを組み合わせて再構成することで、断面画像（スライス）を生成します。スライスを重ね合わせて、3次元画像として体内を立体的に画像化できます。
<figure style="text-align: center; width: 50%; margin: auto;">
  <img src="https://github.com/shizoda/education/assets/34496702/a3eac753-32b0-4c3a-8a3d-ae7df84fbf72">
  <figcaption>"3方向(Axial, Coronal, Sagittal)からスライスした肺の断面画像"</figcaption>
</figure>

#### Hounsfield Unit (H.U.)

CT画像では、各画素の濃度値を Hounsfield Unit（H.U. ハンスフィールド・ユニット）とよばれる単位で表します。水を基準として定義されており、水の密度を0 H.U.、空気を-1000 H.U.としています。異なる組織や物質は特有のH.U.値を持ち、これによりCT画像上での識別が可能になります。

H.U.の値は、CT画像上で異なる組織を特定するのに役立ちます。肺がんのような病変は、周囲の正常な組織とは異なるH.U.値を持つことが多く、これによりCT画像上で識別することが可能になります。

<figure>
  <img src="https://github.com/shizoda/education/assets/34496702/309a03c2-631b-4550-a5cb-738a3f905084", style="width: 50%; height: auto;"><br>
  <figcaption>Hounsfield Unit と、注目したい範囲を閲覧するときの設定。幅を Window Width (WW)、中央を Window Center (WC) で指定すると、その範囲が黒から白までのグラデーションで表現される。</figcaption>
</figure>

## 医用画像処理

医用画像処理 (medical image processing) は、コンピュータによる画像処理を用いて、医用画像から有用な情報を抽出・解析・解釈するために使用される一連の技術です。Computer-Aided Diagnosis (CAD) として診断の精度向上や負担軽減に役立つほか、医学的な知見の取得にも有効です。

- **病変検出 (Lesion Detection)**: 病変検出は、画像内の異常な領域や病変を見つける処理です。たとえばCT画像やMRI画像などで、がん、潰瘍、炎症などの異常を見つけるのに用いられます。

- **位置合わせ (Image Registration)**: 位置合わせは、異なる時間点や異なる撮像方法から得られた複数の画像どうしを合わせるプロセスです。複数の画像を比較しやすくなります。

- **ドメイン変換 (Domain Transfer)**: ドメイン変換は、一方の撮影モダリティで得られた画像を別のモダリティで撮影されたかのように変換する技術です。例えば、CT画像をMRI画像のスタイルに変換することがこれにあたります。この技術は、特定のモダリティでのみ得られる情報を別のモダリティで利用可能にし、診断の柔軟性を高めます。

- **領域抽出 (Region Segmentation)**: セグメンテーションともよばれ、画像から特定の解剖学的領域や病変に対し、その領域を塗ったかのようなラベルをつける処理です。これにより、特定の臓器や病変のサイズ、形状、体積を正確に測定することができます。3次元での可視化や 3D プリントにも有効です。

## セグメンテーションの実践

実際のセグメンテーションプロセスでは、MSDデータセットの肺がん画像を用いて、U-Netモデルをトレーニングします。Pythonを使用してデータの読み込み、前処理、モデルの構築、トレーニングを行います。トレーニングプロセスでは、損失関数、最適化アルゴリズム、評価指標を選択し、モデルのパフォーマンスを評価します。最終的には、モデルを使用して未知のデータに対するセグメンテーションを行い、その結果を分析します。


### MSDデータセット

[MSD（Medical Segmentation Decathlon）データセット](http://medicaldecathlon.com/)は、医用画像において領域を抽出する課題を集めたデータセットであり、10 種類の医用画像が含まれています。

今回用いる肺の課題では、肺のCT画像と、対応する肺がんのラベル（手動で塗られた領域）が提供されています。

### 前処理

まず、症例間で解像度を一致させることが重要です。各画素の表す物理的なサイズが症例によってバラバラでは、正常な処理が困難になるためです。

また、特にCT画像では、前述の Hounsfield Unit（H.U.）に基づく正規化が重要です。
抽出の対象とする組織とそれ以外の組織に十分なコントラストが得られるように H.U. の範囲を決めます。特に機械学習で利用する場合は、その範囲を [0,1] や [-1, 1] などの範囲に正規化するのが一般的です。


## 医用画像データのファイル形式

医用画像は、診断や治療計画において非常に重要な役割を果たします。これらの画像は、PNGやJPEGとして保存できる一般的な2次元画像とは異なり、しばしば3次元以上のデータを含んでいます。

また、写真やイラストなどで一般的な 256 階調よりも遥かに多い階調数が用いられることも多いです。CT 画像での Hounsfield Unit (H.U.) もこれに該当します。

### DICOMとNIfTI形式

医用画像データの一般的なフォーマットとして、Digital Imaging and Communications in Medicine（DICOM; ダイコム）があります。DICOM は、画像データだけでなく、患者情報や撮影条件などの豊富なメタデータも格納できます。しかし、DICOM は各スライス（断面画像）ごとに別々のファイルとして保存されるため、特に3次元以上のデータを扱う際には不便さがあります。

このため、研究や実習などでは Neuroimaging Informatics Technology Initiative (NIfTI; ニフティ) 形式が広く用いられます。NIfTIは、単一のファイル内に3次元または4次元の画像データを格納できるため、特に複数のスライスからなる3次元画像や、時間的変化を含む4次元画像の管理に適しています。またNIfTI形式は、領域のラベルや処理の中間結果などの格納にも便利です。

### NIfTI形式データの可視化

NIfTI形式のデータを効果的に可視化・分析するためには、専門的なソフトウェアが必要です。[3D Slicer](https://www.slicer.org/) や [MITK Workbench](https://www.mitk.org/wiki/The_Medical_Imaging_Interaction_Toolkit_(MITK))、[ITK-SNAP](http://www.itksnap.org/pmwiki/pmwiki.php) などは、これらの医用画像データを扱うためのオープンソースのソフトウェアです。単なる可視化のみならず、フィルタリング、手動・半自動でのセグメンテーション、画像の位置合わせなど、さまざまな高度な画像処理機能を提供します。
