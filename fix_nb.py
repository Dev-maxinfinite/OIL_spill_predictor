import json

def fix_notebook():
    file_path = "Untitled3(1).ipynb"
    
    with open(file_path, "r") as f:
        nb = json.load(f)
        
    for cell in nb.get("cells", []):
        if cell["cell_type"] != "code":
            continue
            
        source = cell["source"]
        source_str = "".join(source)
        
        # 1. Update IMPORTS to include callbacks and Conv2DTranspose
        if "from tensorflow.keras.layers import *" in source_str:
            if "from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau" not in source_str:
                source.append("\nfrom tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau\n")
                
        # 2. Update IMG_SIZE
        if "IMG_SIZE = 128" in source_str:
            new_source = []
            for line in source:
                new_source.append(line.replace("IMG_SIZE = 128", "IMG_SIZE = 256  # Increased size for better resolution feature extraction"))
            cell["source"] = new_source

        # 3. Update build_unet with better architecture (Conv2DTranspose and Dropout)
        if "def build_unet():" in source_str:
            new_code = """def conv_block(x, filters, apply_dropout=False):
    x = Conv2D(filters, 3, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Conv2D(filters, 3, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    if apply_dropout:
        x = Dropout(0.3)(x)
    return x

def build_unet():
    inputs = Input((IMG_SIZE, IMG_SIZE, 3))

    # Encoder
    c1 = conv_block(inputs, 64)
    p1 = MaxPooling2D()(c1)

    c2 = conv_block(p1, 128)
    p2 = MaxPooling2D()(c2)

    c3 = conv_block(p2, 256)
    p3 = MaxPooling2D()(c3)

    c4 = conv_block(p3, 512, apply_dropout=True)
    p4 = MaxPooling2D()(c4)

    # Bridge
    c5 = conv_block(p4, 1024, apply_dropout=True)

    # Decoder
    u6 = Conv2DTranspose(512, 2, strides=2, padding="same")(c5)
    u6 = Concatenate()([u6, c4])
    c6 = conv_block(u6, 512)

    u7 = Conv2DTranspose(256, 2, strides=2, padding="same")(c6)
    u7 = Concatenate()([u7, c3])
    c7 = conv_block(u7, 256)

    u8 = Conv2DTranspose(128, 2, strides=2, padding="same")(c7)
    u8 = Concatenate()([u8, c2])
    c8 = conv_block(u8, 128)

    u9 = Conv2DTranspose(64, 2, strides=2, padding="same")(c8)
    u9 = Concatenate()([u9, c1])
    c9 = conv_block(u9, 64)

    outputs = Conv2D(1, 1, activation="sigmoid")(c9)

    model = Model(inputs, outputs)
    return model

model = build_unet()
model.summary()
"""
            cell["source"] = [new_code]

        # 4. Add Callbacks to model.fit
        if "history = model.fit(" in source_str:
            new_code = """callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ModelCheckpoint('/content/drive/MyDrive/oil_spill_best_model.h5', monitor='val_loss', save_best_only=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
]

history = model.fit(
    X_train, Y_train,
    validation_data=(X_val, Y_val),
    epochs=100,
    batch_size=16,
    callbacks=callbacks
)
"""
            cell["source"] = [new_code]

    with open(file_path, "w") as f:
        json.dump(nb, f, indent=2)

if __name__ == "__main__":
    fix_notebook()
    print("Notebook fixed successfully!")
