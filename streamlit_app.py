import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Title for the Streamlit app
st.title("NDVI Analysis")

# Upload the TIF image
# uploaded_file = st.file_uploader("Upload a TIF file", type=["tif", "tiff"])
uploaded_file = 'data/ndvi_cropped_5000_6000.tif'

if uploaded_file is not None:
    # Read the TIF file
    with rasterio.open(uploaded_file) as src:
        st.write("Image loaded successfully")
        
        # Display basic image info
        st.write(f"Image width: {src.width}")
        st.write(f"Image height: {src.height}")
        st.write(f"Number of bands: {src.count}")
        
        # Check if the file contains at least 2 bands (Red and NIR)
        if src.count < 2:
            st.error("The TIF file must contain at least two bands for NDVI calculation.")
        else:
            # Read the bands for NDVI calculation
            red_band = src.read(1).astype(float)  # Assuming red band is the first one
            nir_band = src.read(2).astype(float)  # Assuming NIR band is the second one
            
            # Calculate NDVI
            ndvi = (nir_band - red_band) / (nir_band + red_band)
            ndvi = np.clip(ndvi, -1, 1)  # Clipping the NDVI values between -1 and 1

            # Display NDVI image
            st.subheader("NDVI Image")
            fig, ax = plt.subplots()
            cax = ax.imshow(ndvi, cmap='RdYlGn')
            fig.colorbar(cax, ax=ax)
            st.pyplot(fig)

            # Display histogram of NDVI values
            st.subheader("NDVI Histogram")
            fig, ax = plt.subplots()
            ax.hist(ndvi.flatten(), bins=50, color='green', alpha=0.7)
            st.pyplot(fig)