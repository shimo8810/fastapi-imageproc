const imageInput = document.getElementById("image-input");
const postBtn = document.getElementById("post-btn");

let imageFile = null;

imageInput.addEventListener("change", () => {
  if (imageInput.files.length > 0) {
    imageFile = imageInput.files[0];
    document.getElementById("preview-img").src = URL.createObjectURL(imageFile);
  }
});

postBtn.addEventListener("click", () => {
  //
  if (!imageFile) {
    console.error("no image file");
    return;
  }

  const body = new FormData();
  body.append("files", imageFile);

  fetch("/api/image-processing", {
    method: "POST",
    body: body,
  })
    .then((resp) => {
      const reader = resp.body.getReader();

      return new ReadableStream({
        start(controller) {
          return pump();

          function pump() {
            return reader.read().then(({ done, value }) => {
              if (done) {
                controller.close();
                return;
              }
              controller.enqueue(value);
              return pump();
            });
          }
        },
      });
    })
    .then((stream) => new Response(stream))
    .then((resp) => resp.blob())
    .then((blob) => {
      document.getElementById("output-img").src = URL.createObjectURL(blob);
    });
});
