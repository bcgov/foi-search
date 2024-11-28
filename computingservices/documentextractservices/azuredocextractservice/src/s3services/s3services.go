package s3services

import (
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/spf13/viper"
)

// use viper package to read .env file
// return the value of the key
func viperEnvVariable(key string) string {

	// SetConfigFile explicitly defines the path, name and extension of the config file.
	// Viper will use this and not check any of the config paths.
	// .env - It will search for the .env file in the current directory
	viper.SetConfigFile("./.env")

	// Find and read the config file
	err := viper.ReadInConfig()

	if err != nil {
		log.Fatalf("Error while reading config file %s", err)
	}

	// viper.Get() returns an empty interface{}
	// to get the underlying type of the key,
	// we have to do the type assertion, we know the underlying value is string
	// if we type assert to other type it will throw an error
	value, ok := viper.Get(key).(string)

	// If the type is a string then ok will be true
	// ok will make sure the program not break
	if !ok {
		log.Fatalf("Invalid type assertion")
	}

	return value
}

func GetFilefroms3(s3relativefileurl string, bucketname string) string {
	// Define S3-compatible storage endpoint and credentials
	endpoint := viperEnvVariable("s3endpoint") // Update with your S3-compatible endpoint
	accessKey := viperEnvVariable("s3accesskey")
	secretKey := viperEnvVariable("s3secretkey")
	bucketName := "/" + bucketname + "/"
	objectKey := s3relativefileurl
	region := viperEnvVariable("s3region") // e.g., "us-east-1"
	s3forcepathstyle, _ := strconv.ParseBool(viperEnvVariable("s3forcepathstyle"))
	expiry := 15 * time.Minute // Presigned URL expiry time
	fmt.Println("accessKey:", accessKey)
	fmt.Println("secretKey:", secretKey)
	fmt.Println("bucketName:", bucketName)
	fmt.Println("s3forcepathstyle:", s3forcepathstyle)
	url, err := generatePresignedURL(endpoint, accessKey, secretKey, bucketName, objectKey, region, expiry)
	if err != nil {
		log.Fatalf("Error generating presigned URL: %v", err)
	}

	fmt.Println("Presigned URL:", url)
	return url
}

func generatePresignedURL(endpoint, accessKey, secretKey, bucketName, objectKey, region string, expiry time.Duration) (string, error) {
	// Create a new session with the provided credentials
	sess, err := session.NewSession(&aws.Config{
		Region:      aws.String(region),
		Endpoint:    aws.String(endpoint), // S3-compatible endpoint (like S3 Browser)
		Credentials: credentials.NewStaticCredentials(accessKey, secretKey, ""),
	})
	if err != nil {
		return "", fmt.Errorf("failed to create session: %v", err)
	}
	// Create a new S3 client
	svc := s3.New(sess)
	// Prepare the GetObjectRequest
	req, _ := svc.GetObjectRequest(&s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
	})
	// Generate the presigned URL
	presignedURL, err := req.Presign(expiry)
	if err != nil {
		return "", fmt.Errorf("failed to generate presigned URL: %v", err)
	}
	return presignedURL, nil
}
